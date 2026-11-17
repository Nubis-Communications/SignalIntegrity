// SignalIntegrity Electron shell
//
// Starts the SignalIntegrity web server (python -m SignalIntegrity.Server) as a sidecar process,
// waits for the JSON ready line it prints on stdout and points a hardened BrowserWindow at the
// URL it reports. The window only ever shows the local loading page or the sidecar's own origin.
// The sidecar is started with --exit-with-stdin, so it also exits if this process dies abruptly.
'use strict';

const { app, BrowserWindow, Menu, dialog, session, shell } = require('electron');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const READY_TIMEOUT_MS = 90000;
const SMOKE_TIMEOUT_MS = 120000;
const TITLE_BAR_HEIGHT = 32;
const PANE_WINDOW = /^si-pane-[a-z]+$/;

let sidecar = null;
let serverOrigin = null;
let mainWindow = null;
let pendingProject = null;  // macOS delivers file-association opens through 'open-file'

const smokeTest = process.argv.includes('--smoke-test');
// the smoke test changes the pane layout, so it must not use the real settings
const smokeSettings = smokeTest ? fs.mkdtempSync(path.join(os.tmpdir(), 'si-electron-smoke-')) : null;

// ---------- locating Python and the SignalIntegrity sources

function sourceRoot() {
  if (process.env.SIGNALINTEGRITY_ROOT) return path.resolve(process.env.SIGNALINTEGRITY_ROOT);
  // in a checkout this file lives in <root>/Electron
  const root = path.resolve(__dirname, '..');
  return fs.existsSync(path.join(root, 'SignalIntegrity', 'Server')) ? root : null;
}

function pythonCandidates(root) {
  const candidates = [];
  if (process.env.SIGNALINTEGRITY_PYTHON) candidates.push([process.env.SIGNALINTEGRITY_PYTHON, []]);
  if (root) {
    const venv = process.platform === 'win32'
      ? path.join(root, '.venv', 'Scripts', 'python.exe')
      : path.join(root, '.venv', 'bin', 'python');
    if (fs.existsSync(venv)) candidates.push([venv, []]);
  }
  candidates.push(['python', []], ['python3', []]);
  if (process.platform === 'win32') candidates.push(['py', ['-3']]);
  return candidates;
}

// ---------- the sidecar

function projectFromArgs(argv) {
  // packaged: <exe> [file]; development: electron . [file]
  const args = argv.slice(app.isPackaged ? 1 : 2).filter((a) => !a.startsWith('-'));
  const project = args.find((a) => a.toLowerCase().endsWith('.si'));
  return project ? path.resolve(project) : null;
}

function startCandidate(program, prefix, root, project) {
  return new Promise((resolve, reject) => {
    const env = { ...process.env };
    delete env.SIGNALINTEGRITY_SERVER_TOKEN;  // the server always makes a fresh token
    if (smokeSettings) env.SIGNALINTEGRITY_GUI_SETTINGS = smokeSettings;
    if (root) env.PYTHONPATH = env.PYTHONPATH ? root + path.delimiter + env.PYTHONPATH : root;
    const args = [...prefix, '-m', 'SignalIntegrity.Server', '--exit-with-stdin'];
    if (project) args.push(project);
    let child;
    try {
      child = spawn(program, args, { cwd: root || undefined, env, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
    } catch (e) {
      reject(new Error(`${program}: ${e.message}`));
      return;
    }
    let stdout = '';
    let stderr = '';
    let settled = false;
    const finish = (error, url) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (error) {
        child.kill();
        reject(error);
      } else {
        resolve({ child, url });
      }
    };
    const timer = setTimeout(() => finish(new Error(`${program}: server did not report ready`)), READY_TIMEOUT_MS);
    child.on('error', (e) => finish(new Error(`${program}: ${e.message}`)));
    child.on('exit', (code) => {
      const detail = stderr.trim().split(/\r?\n/).slice(-5).join('\n');
      finish(new Error(`${program}: exited with code ${code}` + (detail ? `\n${detail}` : '')));
    });
    child.stderr.on('data', (d) => {
      stderr = (stderr + d).slice(-8000);  // keep draining so the pipe never fills
    });
    child.stdout.on('data', (d) => {
      if (settled) return;  // keep draining after the ready line
      stdout += d;
      const newline = stdout.indexOf('\n');
      if (newline < 0) return;
      try {
        const url = new URL(JSON.parse(stdout.slice(0, newline)).signalintegrity_server.url);
        if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1') throw new Error('unexpected server url');
        finish(null, url);
      } catch (e) {
        finish(new Error(`${program}: bad ready line (${e.message})`));
      }
    });
  });
}

async function startServer(project) {
  const root = sourceRoot();
  const errors = [];
  for (const [program, prefix] of pythonCandidates(root)) {
    try {
      return await startCandidate(program, prefix, root, project);
    } catch (e) {
      errors.push(e.message);
    }
  }
  throw new Error('Tried:\n' + errors.join('\n'));
}

function stopServer() {
  if (sidecar && sidecar.exitCode === null) {
    sidecar.stdin.end();  // --exit-with-stdin makes the server shut down cleanly
    sidecar.kill();
  }
  sidecar = null;
}

// ---------- the window

function isAllowed(target) {
  try {
    const url = new URL(target);
    if (url.protocol === 'file:') return url.pathname.endsWith('/loading/index.html');
    return serverOrigin !== null && url.origin === serverOrigin;
  } catch (e) {
    return false;
  }
}

function hardenSession() {
  // the UI needs no camera, microphone, notifications, geolocation ...
  session.defaultSession.setPermissionRequestHandler((wc, permission, callback) => callback(false));
  session.defaultSession.setPermissionCheckHandler(() => false);
}

const webPreferences = { contextIsolation: true, nodeIntegration: false, sandbox: true, webSecurity: true, spellcheck: false };
const iconPath = path.join(__dirname, 'icons', process.platform === 'win32' ? 'icon.ico' : 'icon.png');

// every page (the main window and pane windows) gets the same rules
function guard(wc) {
  wc.on('will-navigate', (event, url) => {
    if (!isAllowed(url)) event.preventDefault();
  });
  wc.on('will-redirect', (event, url) => {
    if (!isAllowed(url)) event.preventDefault();
  });
  wc.on('will-attach-webview', (event) => event.preventDefault());
  wc.setWindowOpenHandler(({ url, frameName }) => {
    // "Move to New Window": a blank same-origin window the main page fills with one of its panes
    if (mainWindow && wc === mainWindow.webContents && url === 'about:blank' && PANE_WINDOW.test(frameName)) {
      return {
        action: 'allow',
        overrideBrowserWindowOptions: {
          show: !smokeTest, icon: iconPath, autoHideMenuBar: true, minWidth: 220, minHeight: 120,
          backgroundColor: mainWindow.getBackgroundColor(), webPreferences,
        },
      };
    }
    // help pages are opened by the server itself; anything else on the web goes to the browser
    if (/^https?:/.test(url) && !isAllowed(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
}

// tints the window controls drawn over the custom title bar to match the theme
function titleBarColors(color) {
  const m = /^#([0-9a-f]{6})$/i.exec(color || '');
  if (!m) return null;
  const v = parseInt(m[1], 16);
  const luminance = (0.299 * (v >> 16) + 0.587 * ((v >> 8) & 255) + 0.114 * (v & 255)) / 255;
  return { color, symbolColor: luminance > 0.55 ? '#333333' : '#e0e0e0', height: TITLE_BAR_HEIGHT };
}

function createWindow() {
  const mac = process.platform === 'darwin';
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 500,
    show: !smokeTest,
    title: 'SignalIntegrity',
    icon: iconPath,
    backgroundColor: '#f3f3f3',
    titleBarStyle: 'hidden',
    ...(mac ? { trafficLightPosition: { x: 10, y: 9 } } : { titleBarOverlay: titleBarColors('#f3f3f3') }),
    webPreferences,
  });
  if (!mac) {
    win.webContents.on('did-change-theme-color', (event, color) => {
      const colors = titleBarColors(color);
      if (colors) win.setTitleBarOverlay(colors);
    });
  }
  win.loadFile(path.join(__dirname, 'loading', 'index.html'));
  return win;
}

function showStartupError(win, message) {
  if (smokeTest) {
    report({ ok: false, error: message });
    return;
  }
  win.webContents.executeJavaScript(`window.showStartupError(${JSON.stringify(message)})`).catch(() => {
    dialog.showErrorBox('SignalIntegrity', message);
  });
}

function applicationMenu() {
  // the web UI draws its own menus; macOS still needs an app menu for the standard shortcuts
  if (process.platform !== 'darwin') return null;
  return Menu.buildFromTemplate([{ role: 'appMenu' }, { role: 'editMenu' }, { role: 'windowMenu' }]);
}

// ---------- smoke test (npm run smoke)

function report(result) {
  process.stdout.write(JSON.stringify(result) + '\n');
  stopServer();
  if (smokeSettings) fs.rmSync(smokeSettings, { recursive: true, force: true });
  app.exit(result.ok ? 0 : 1);  // app.quit() would ignore the exit code
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// pops the Device Properties pane out to a window, closes that window, then closes the pane
async function paneControls(win) {
  const js = (code) => win.webContents.executeJavaScript(code);
  const where = `(() => { const p = document.querySelector('[data-pane="properties"]');
    return !p ? 'window' : p.closest('#paneStash') ? 'closed' : p.closest('.dock') ? 'docked' : 'other'; })()`;
  const result = { before: await js(where) };
  await js(`document.querySelector('[data-pane="properties"] .pane-action.pop-out').click(); 0`);
  await sleep(800);
  const children = BrowserWindow.getAllWindows().filter((w) => w !== win);
  result.poppedOut = await js(where);
  result.paneWindows = children.length;
  result.paneWindowTitle = children.length ? children[0].getTitle() : null;
  for (const child of children) child.close();
  await sleep(1200);
  result.afterWindowClosed = await js(where);
  await js(`document.querySelector('[data-pane="properties"] .pane-action.close').click(); 0`);
  await sleep(300);
  result.afterClose = await js(where);
  result.ok = result.before === 'docked' && result.poppedOut === 'window' && result.paneWindows === 1 &&
    result.afterWindowClosed === 'docked' && result.afterClose === 'closed';
  return result;
}

async function runSmokeTest(win, project) {
  const deadline = Date.now() + SMOKE_TIMEOUT_MS;
  const probe = `(() => ({
    title: document.title,
    toolbarButtons: document.querySelectorAll('#toolbar button').length,
    menus: document.querySelectorAll('#menubar button').length,
    drawn: document.querySelectorAll('#viewport > *').length,
    skin: document.documentElement.classList.contains('skin-vscode'),
    lineIcons: document.querySelectorAll('#toolbar svg.line-icon').length,
    origin: location.origin }))()`;
  while (Date.now() < deadline) {
    try {
      const state = await win.webContents.executeJavaScript(probe);
      if (state.toolbarButtons > 0 && state.menus > 0 && (!project || state.drawn > 0)) {
        const node = await win.webContents.executeJavaScript('typeof require + "/" + typeof process');
        const panes = await paneControls(win);
        // navigating away from the server origin must be refused
        await win.webContents.executeJavaScript('location.href = "http://127.0.0.1:1/"; 0');
        await sleep(500);
        const stayed = new URL(win.webContents.getURL()).origin === serverOrigin;
        const skinned = state.skin && state.lineIcons === state.toolbarButtons;
        report({ ok: node === 'undefined/undefined' && stayed && skinned && panes.ok,
          nodeInPage: node, navigationBlocked: stayed, panes, ...state });
        return;
      }
    } catch (e) {
      // page still loading
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  report({ ok: false, error: 'UI did not finish loading' });
}

// ---------- application lifecycle

app.on('open-file', (event, file) => {
  event.preventDefault();
  pendingProject = file;
});

app.on('web-contents-created', (event, contents) => guard(contents));

app.whenReady().then(async () => {
  hardenSession();
  Menu.setApplicationMenu(applicationMenu());
  mainWindow = createWindow();
  mainWindow.on('closed', () => {
    for (const w of BrowserWindow.getAllWindows()) w.close();
  });
  const project = pendingProject || projectFromArgs(process.argv);
  try {
    const started = await startServer(project);
    sidecar = started.child;
    serverOrigin = started.url.origin;
    sidecar.on('exit', () => {
      sidecar = null;
      if (mainWindow && !mainWindow.isDestroyed()) mainWindow.close();
    });
    if (!mainWindow || mainWindow.isDestroyed()) {
      stopServer();
      return;
    }
    const url = new URL(started.url.href);
    url.search = '?skin=vscode&titlebar=custom';
    await mainWindow.loadURL(url.href);
    if (smokeTest) runSmokeTest(mainWindow, project);
  } catch (e) {
    if (mainWindow && !mainWindow.isDestroyed()) showStartupError(mainWindow, e.message);
  }
});

app.on('window-all-closed', () => app.quit());
app.on('will-quit', stopServer);
process.on('exit', stopServer);
