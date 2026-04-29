const { app, BrowserWindow } = require('electron');
const path = require('path');

let win;

function createWindow() {
    win = new BrowserWindow({
        width: 500,
        height: 550,
        resizable: false,
        webPreferences: {
            nodeIntegration: false
        }
    });
    win.loadFile('snake.html');
    win.setMenu(null);
}

app.whenReady().then(createWindow);