import sys, os, json, venv, shutil
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from console import Console, ConsoleGui
from shortcuts import ShortcutGui, Shortcut
from automation import Automator
from utils import ShortcutCreator

OS = sys.platform

class MainWindow(QWidget):
    def __init__(self):
        super().__init__(None)

        self.setWindowTitle("Shortcuts")
        self.setWindowIcon(QIcon("src/shortcuts.png"))

        self.icon = QSystemTrayIcon(self.windowIcon(), self)
        self.icon.activated.connect(self.trayTriggered)
        menu = QMenu(self)
        menu.setStyleSheet("color:white;")
        show = QAction("Show", menu)
        show.triggered.connect(self.show)
        
        hide = QAction("Hide", menu)
        hide.triggered.connect(self.hide)
        
        quit = QAction("Quit", menu)
        quit.triggered.connect(QApplication.quit)

        menu.addActions([show, hide, quit])
        self.icon.setContextMenu(menu)
        self.icon.show()
        
        self._width = 500
        self._height = 500
        self.setStyleSheet("background-color:rgb(24,24,24);")
        self.setGeometry(0, 0, self._width, self._height)
        self.setContentsMargins(0,0,0,0)
        
        self.setAutoFillBackground(True)
        self.console_gui = ConsoleGui(self)
        self.console = Console(self.console_gui)

        self.shortcuts, self.shortcut_guis = self.getShortcuts()
        self.automator = Automator(self.shortcuts)

        self.reload_icon = QIcon("src/reload.png")
        self.reload_button = QPushButton(self.reload_icon, "", self)
        self.reload_button.setStyleSheet("background-color:rgb(24,24,24); border:none;")
        self.reload_button.clicked.connect(self.reload)


        self.shortcut_button = QPushButton("+", self)
        self.shortcut_button.setStyleSheet("background-color:rgb(24,24,24); color:white; border:none; font-size:30px;")
        
        self.shortcut_creator = ShortcutCreator(self)
        
        self.shortcut_button.clicked.connect(self.shortcut_creator.show)
        self.show()
    def trayTriggered(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
    def getShortcuts(self):
        os.makedirs("shortcut", exist_ok=True)
        sd = os.path.join(os.getcwd(), "shortcut")
        paths = [
            {
                "name":"file",
                "path":"file/(any)"
            },
            {
                "name":"info_file",
                "path":"info.json"
            },
            {
                "name":"exe",
                "path":["venv/Scripts/python.exe", "venv/bin/python"]
            },
            {
                "name":"icon",
                "path":"icon/(any)"
            },
            {
                "name":"automation",
                "path":".auto"
            }
            ]
        shortcuts = []
        guis = []
        for d in os.listdir("shortcut"):
            d = os.path.join(sd, d)
            if os.path.isdir(d):
                info = {}
                info['dir_name'] = d
                for path in paths:
                    if type(path['path']) != list:
                        new_path = os.path.join(d, path['path'])
                        dir_name = os.path.dirname(new_path)
                        print(f"\n{new_path}")
                        if "(any)" not in new_path and os.path.exists(new_path):
                            info[path['name']] = new_path
                        elif "(any)" in new_path and os.path.exists(dir_name):
                            new_path = os.path.join(dir_name, os.listdir(os.path.dirname(new_path))[0])
                            info[path['name']] = new_path
                        else:
                            info[path['name']] = None
                    else:
                        for p in path['path']:
                            new_path = os.path.join(d, p)
                            info[path['name']] = new_path if os.path.exists(new_path) else "bin/python/python.exe" if OS == "win32" else "bin/python/python"
                shortcut = Shortcut(info, self.console)
                shortcuts.append(shortcut)
                shortcut_gui = ShortcutGui(shortcut, self)
                guis.append(shortcut_gui)
        return shortcuts, guis
    
    def resizeEvent(self, event):
        column = 0

        total_width = self.width()
        total_height = self.height()

        self.reload_button.setGeometry(0, total_height - 30, 30, 30)

        self.console_gui.setGeometry(0,0, total_width, total_height)
        self.shortcut_creator.setGeometry(0,0, total_width, total_height)

        self.shortcut_button.setGeometry(total_width - 30, total_height - 40, 30, 40)
        padding = 10
        cols = 3
        rows = 3

        s_width = (total_width - (cols + 1) * padding) // cols
        s_height = (total_height - (rows + 1) * padding) // rows

        x = padding
        y = padding

        for i, s in enumerate(self.shortcut_guis):
            if column == cols:
                y += s_height + padding
                x = padding
                column = 0

            s.setGeometry(x, y, s_width, s_height)

            x += s_width + padding
            column += 1

        super().resizeEvent(event)
    def reload(self):
        for s in self.shortcuts:
            s.deleteLater()
        for s in self.shortcut_guis:
            s.setVisible(False)
            s.deleteLater()
        self.shortcuts, self.shortcut_guis = self.getShortcuts()
        self.automator.shortcuts = self.shortcuts
        self.automator.reload()                    
        self.resizeEvent(None)
    def closeEvent(self, event):
        event.ignore()
        self.hide()
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    # creator = ShortcutCreator(None)
    sys.exit(app.exec_())