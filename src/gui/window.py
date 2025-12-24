import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QSystemTrayIcon, QGridLayout
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtCore import Qt
from src.utils.config import getIniConfig
from src.gui.trayicon import TrayIcon
from src.core.shortcutmanager import ShortcutManager
from src.core.shortcuts import ShortcutGui
OS = sys.platform

class MainWindow(QWidget):
    def __init__(self):
        super().__init__(None)

        self.setWindowTitle("Shortcuts")
        self.setWindowIcon(QIcon("resources/shortcuts.png"))

        config = getIniConfig("options.ini")
        self.minOnStart = config.get("Window", "MinOnStart").lower()
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

        self.icon = TrayIcon(self.windowIcon(), self)
        self.icon.activated.connect(self.trayTriggered)

        self.icon.show()
        


        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(25)
        self.setLayout(self.grid_layout)

        self.shortcut_manager = ShortcutManager("./shortcut", self)

        column = 0
        row = 0
        for s in self.shortcut_manager.getShortcuts():
            if column == 3:
                row += 1
                column = 0
            gui = s.getGui()
            self.grid_layout.addWidget(gui, row, column)
            gui.show()
            self.grid_layout.update()
            column += 1


        # self.reload_icon = QIcon("resources/reload.png")
        # self.reload_button = QPushButton(self.reload_icon, "", self)
        # self.reload_button.setStyleSheet("background-color:rgb(24,24,24); border:none;")
        # self.reload_button.clicked.connect(self.reload)


        if self.minOnStart and self.minOnStart == "false":
            self.show()
            self.resizeEvent(None)
    def trayTriggered(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def reload(self):
        self.shortcut_manager.reload()
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
    