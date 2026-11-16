// called by the Tauri shell when the Python server cannot be started
window.showStartupError = function (message) {
  document.getElementById('message').textContent = 'The SignalIntegrity engine could not be started.';
  const error = document.getElementById('error');
  error.textContent = message;
  error.style.display = 'block';
};
