import sys, os, json, venv, shutil
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QGuiApplication
from shortcuts import ShortcutGui, Shortcut
from utils import ShortcutCreator
from configparser import ConfigParser

OS = sys.platform

class MainWindow(QWidget):
    def __init__(self):
        super().__init__(None)

        self.setWindowTitle("Shortcuts")
        self.setWindowIcon(QIcon("resources/shortcuts.png"))
        config = ConfigParser()
        config.read("options.ini")
        self.minOnStart = True if config.get("Window", "MinOnStart").lower() == "true" else False
        self.background_color = config.get("Window", "BackgroundColor") or "rgb(24,24,24)"
        screen = QGuiApplication.primaryScreen()
        self._width = int(config.get("Window", "Width")) or int(screen.size().width() // 1.5)
        self._height = int(config.get("Window", "Height")) or int(screen.size().height() // 1.5)
        self.setStyleSheet(f"background-color:{self.background_color};")
        self.resize(self._width, self._height)
        self.setContentsMargins(0,0,0,0)
        
        self.setAutoFillBackground(True)
        self._scroll = 0
        self.pause = False
        self.icon = QSystemTrayIcon(self.windowIcon(), self)
        self.icon.activated.connect(self.trayTriggered)
        menu = QMenu(self)
        show = QAction("Show", menu)
        show.triggered.connect(self.show)
        
        hide = QAction("Hide", menu)
        hide.triggered.connect(self.hide)
        
        quit = QAction("Quit", menu)
        quit.triggered.connect(QApplication.quit)

        menu.addActions([show, hide, quit])
        self.icon.setContextMenu(menu)
        self.icon.show()
        

        self.shortcuts = self.getShortcuts()
        # self.automator = Automator(self.shortcuts)

        self.reload_icon = QIcon("resources/reload.png")
        self.reload_button = QPushButton(self.reload_icon, "", self)
        self.reload_button.setStyleSheet("background-color:rgb(24,24,24); border:none;")
        self.reload_button.clicked.connect(self.reload)

        self.shortcut_button = QPushButton("+", self)
        self.shortcut_button.setStyleSheet("background-color:rgb(24,24,24); border:none; font-size:30px;")
        
        self.shortcut_creator = ShortcutCreator(None, self)
        
        self.shortcut_button.clicked.connect(self.shortcut_creator.show)
        if not self.minOnStart:
            self.show()
            self.resizeEvent(None)
    def trayTriggered(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def getShortcuts(self):
        os.makedirs("shortcut", exist_ok=True)
        sd = os.path.join(os.getcwd(), "shortcut")

        paths = [
            {"name": "file",       "path": "file/(any)"},
            {"name": "info_file",  "path": "info.json"},
            {"name": "exe",        "path": ["venv/Scripts/python.exe", "venv/bin/python"]},
            {"name": "icon",       "path": "icon/(any)"},
            {"name": "automation", "path": ".auto"},
        ]

        shortcuts = []

        for d in os.listdir(sd):
            d = os.path.join(sd, d)
            if not os.path.isdir(d):
                continue


            shortcut = Shortcut(d, self)
            shortcuts.append(shortcut)


        return shortcuts

    def deleteShortcut(self, shortcut : ShortcutGui):
        for s in self.shortcuts:
            if s.getGui() == shortcut:
                shortcut.hide()
                shortcut.deleteLater()
                self.shortcuts.remove(s)
        self.resizeEvent(None)
    def resizeEvent(self, event):
        if self.pause == False:
            column = 0

            total_width = self.width()
            total_height = self.height()

            self.reload_button.setGeometry(0, total_height - 30, 30, 30)
            
            self.shortcut_creator.setGeometry(0,0, total_width, total_height)

            self.shortcut_button.setGeometry(total_width - 30, total_height - 40, 30, 40)
            padding = 10
            cols = 3
            rows = 3

            s_width = (total_width - (cols + 1) * padding) // cols
            s_height = ((total_height - 30) - (rows + 1) * padding) // rows

            x = padding
            y = padding + self._scroll
            for i, s in enumerate(self.shortcuts):
                if column == cols:
                    y += s_height + padding
                    x = padding
                    column = 0

                s.getGui().setGeometry(x, y, s_width, s_height)

                x += s_width + padding
                column += 1

            super().resizeEvent(event)
    def reload(self):
        for s in self.shortcuts:
            s.deleteLater()
            gui = s.getGui()
            gui.setVisible(False)
            gui.deleteLater()
        self.shortcuts = self.getShortcuts()
        self.resizeEvent(None)
    def closeEvent(self, event):
        if sys.platform != "linux":
            event.ignore()
            self.hide()
    def wheelEvent(self, event):
        if self.pause == False:
            scroll_speed = 30
            
            if event.angleDelta().y() > 0:
                self._scroll = min(0, self._scroll + scroll_speed)
            elif event.angleDelta().y() < 0:
                self._scroll -= scroll_speed
            self.resizeEvent(None)
            super().wheelEvent(event)
    def quit(self):
        self.icon.hide()
    