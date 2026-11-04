'use strict';
const { app, BrowserWindow, shell } = require('electron');
const path = require('node:path');
const fs = require('node:fs');
if (process.env.PORTABLE_EXECUTABLE_DIR) {
  const dataDir = path.join(process.env.PORTABLE_EXECUTABLE_DIR, 'G-word-data');
  fs.mkdirSync(dataDir, { recursive: true });
  app.setPath('userData', dataDir);
}
function createWindow() {
  const win = new BrowserWindow({
    width: 1280, height: 860, minWidth: 760, minHeight: 600,
    show: false, title: 'G-word — Offline Bible', backgroundColor: '#f3f7fc',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false, contextIsolation: true, sandbox: true,
      webSecurity: true, allowRunningInsecureContent: false
    }
  });
  win.once('ready-to-show', () => win.show());
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('https://') || url.startsWith('http://')) shell.openExternal(url).catch(() => {});
    return { action: 'deny' };
  });
  win.webContents.on('will-navigate', (event, url) => {
    if (url !== win.webContents.getURL()) event.preventDefault();
  });
  win.loadFile(path.join(__dirname, '..', 'index.html'));
}
app.whenReady().then(() => {
  app.setAppUserModelId('org.jllvci.payatas.gword');
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
