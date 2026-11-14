// SignalIntegrity desktop shell: starts the SignalIntegrity Python server as a sidecar process
// and shows its token-protected web GUI in a native window.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader, Read};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::{mpsc, Mutex};
use std::time::Duration;

use tauri::{Manager, RunEvent};

const STARTUP_TIMEOUT: Duration = Duration::from_secs(90);

struct Sidecar(Mutex<Option<Child>>);

#[derive(serde::Deserialize)]
struct ReadyLine {
    signalintegrity_server: ServerInfo,
}

#[derive(serde::Deserialize)]
struct ServerInfo {
    url: String,
}

/// python interpreters to try, in order: $SIGNALINTEGRITY_PYTHON, the checkout's .venv, then python, python3, py -3
fn python_candidates() -> Vec<(String, Vec<String>)> {
    let mut candidates = Vec::new();
    if let Ok(python) = std::env::var("SIGNALINTEGRITY_PYTHON") {
        candidates.push((python, vec![]));
    }
    if let Some(root) = source_root() {
        let venv = root.join(".venv");
        let python = if cfg!(windows) { venv.join("Scripts").join("python.exe") } else { venv.join("bin").join("python") };
        if python.is_file() {
            candidates.push((python.to_string_lossy().into_owned(), vec![]));
        }
    }
    candidates.push(("python".into(), vec![]));
    candidates.push(("python3".into(), vec![]));
    if cfg!(windows) {
        candidates.push(("py".into(), vec!["-3".into()]));
    }
    candidates
}

/// source checkout to put on PYTHONPATH: $SIGNALINTEGRITY_ROOT, else the repository this was built from
fn source_root() -> Option<PathBuf> {
    let root = std::env::var("SIGNALINTEGRITY_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("..").join(".."));
    root.join("SignalIntegrity").join("Server").is_dir().then_some(root)
}

fn spawn_server(project: Option<String>) -> Result<(Child, String), String> {
    let mut errors = Vec::new();
    for (program, prefix) in python_candidates() {
        let mut command = Command::new(&program);
        command.args(&prefix).args(["-m", "SignalIntegrity.Server"]);
        if let Some(project) = &project {
            command.arg(project);
        }
        if let Some(root) = source_root() {
            let mut paths = vec![root];
            if let Some(existing) = std::env::var_os("PYTHONPATH") {
                paths.extend(std::env::split_paths(&existing));
            }
            if let Ok(joined) = std::env::join_paths(paths) {
                command.env("PYTHONPATH", joined);
                // keeps a stale installed SignalIntegrity from shadowing the checkout
                command.current_dir(source_root().unwrap());
            }
        }
        command.env_remove("SIGNALINTEGRITY_SERVER_TOKEN");
        command.stdin(Stdio::null()).stdout(Stdio::piped()).stderr(Stdio::piped());
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x0800_0000;
            command.creation_flags(CREATE_NO_WINDOW);
        }
        let mut child = match command.spawn() {
            Ok(child) => child,
            Err(e) => {
                errors.push(format!("{program}: {e}"));
                continue;
            }
        };
        let stdout = child.stdout.take().expect("stdout is piped");
        let mut stderr = child.stderr.take().expect("stderr is piped");
        let (tx, rx) = mpsc::channel();
        std::thread::spawn(move || {
            let mut reader = BufReader::new(stdout);
            let mut line = String::new();
            let _ = tx.send(reader.read_line(&mut line).map(|_| line));
            // keep draining so the server never blocks on a full pipe
            let _ = std::io::copy(&mut reader, &mut std::io::sink());
        });
        let (etx, erx) = mpsc::channel();
        std::thread::spawn(move || {
            let mut text = String::new();
            let _ = stderr.read_to_string(&mut text);
            let _ = etx.send(text);
        });
        match rx.recv_timeout(STARTUP_TIMEOUT) {
            Ok(Ok(line)) => match serde_json::from_str::<ReadyLine>(line.trim()) {
                Ok(ready) => return Ok((child, ready.signalintegrity_server.url)),
                Err(_) => {
                    let _ = child.kill();
                    let detail = erx.recv_timeout(Duration::from_secs(2)).unwrap_or_default();
                    errors.push(format!("{program}: server did not start\n{}", detail.trim()));
                }
            },
            _ => {
                let _ = child.kill();
                errors.push(format!("{program}: server did not report ready"));
            }
        }
    }
    Err(format!(
        "Could not start the SignalIntegrity server.\n\nInstall SignalIntegrity for Python 3 \
         (pip install SignalIntegrity) or set SIGNALINTEGRITY_PYTHON to the interpreter to use.\n\n{}",
        errors.join("\n\n")
    ))
}

fn main() {
    let project = std::env::args().nth(1).map(|p| {
        std::path::absolute(&p).map(|a| a.to_string_lossy().into_owned()).unwrap_or(p)
    });
    let app = tauri::Builder::default()
        .manage(Sidecar(Mutex::new(None)))
        .setup(move |app| {
            let handle = app.handle().clone();
            std::thread::spawn(move || {
                let window = handle.get_webview_window("main").expect("main window");
                match spawn_server(project) {
                    Ok((child, url)) => {
                        *handle.state::<Sidecar>().0.lock().unwrap() = Some(child);
                        match tauri::Url::parse(&url) {
                            Ok(url) => {
                                let _ = window.navigate(url);
                            }
                            Err(e) => show_error(&window, &e.to_string()),
                        }
                    }
                    Err(message) => show_error(&window, &message),
                }
            });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building the SignalIntegrity desktop app");

    app.run(|handle, event| {
        if let RunEvent::Exit = event {
            if let Some(mut child) = handle.state::<Sidecar>().0.lock().unwrap().take() {
                let _ = child.kill();
                let _ = child.wait();
            }
        }
    });
}

fn show_error(window: &tauri::WebviewWindow, message: &str) {
    let json = serde_json::to_string(message).unwrap_or_else(|_| "\"error\"".into());
    let _ = window.eval(&format!("window.showStartupError && window.showStartupError({json})"));
}
