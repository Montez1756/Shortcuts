import os, json
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QColor, QFont, QFontDatabase
from gui import tint_pixmap
class Shortcut(QObject):
    def __init__(self, info : dict, console):
        super().__init__(None)
        self.info = info
        self.console = console
        self.auto = False
        self.init()
        self.good = False
        if self.auto:
            if getattr(self, 'file', None) and getattr(self, 'automation', None):
                self.good = True
        elif getattr(self, 'file', None):
            self.good = True

    def init(self):
        for key in self.info.keys():
            if key == "automation" and self.info[key]:
                self.auto = True
            setattr(self, key, self.info[key])
        if self.info_file:
            info_ob = {}
            with open(self.info_file, "r") as file:
                info_ob = json.loads(file.read())
            for key in info_ob.keys():
                setattr(self, key, info_ob[key])
    def run(self, args):
        if self.good:
            self.console.run(self, args)
            
class ShortcutGui(QWidget):
    def __init__(self, shortcut : Shortcut = None, parent : QWidget = None):
        super().__init__(parent)

        self.setStyleSheet("background-color:rgb(75,75,75); border-radius:10px; color:white;")
        self.setContentsMargins(10,10,10,10)
        self._parent = parent
        self.shortcut = shortcut
        self.good = self.shortcut.good
        
        # layout = QVBoxLayout(self)
        # self.setLayout(layout)
        
        self.name = QLabel(getattr(self.shortcut, 'name', 'Unnamed'), self)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(self.name)
        font = QFont("Ariel", 12,10,False)
        self.name.setFont(font)

        if self.shortcut.icon:
            self.icon_pixmap = QPixmap(self.shortcut.icon)
            if not self.icon_pixmap.isNull():
                self.icon = QLabel(self)
                self.icon.setPixmap(self.icon_pixmap)
        if not self.good:
            self.lock_pixmap = QPixmap('src/lock.png')
            self.lock_pixmap = tint_pixmap(self.lock_pixmap, QColor(200, 0, 0))
            if not self.lock_pixmap.isNull():
                self.lock = QLabel(self)
                self.lock.setStyleSheet("background-color:transparent;")
                self.lock.setPixmap(self.lock_pixmap)

        self.setAcceptDrops(True)
        self.setVisible(True)
    def dropEvent(self, a0):
        urls = a0.mimeData().urls()
        self.shortcut.run(urls)
            
    def dragEnterEvent(self, a0):
        if a0.mimeData().hasUrls():
            a0.acceptProposedAction()
        else:
            a0.ignore()
    def resizeEvent(self, event):
        width = self.width()
        height = self.height()
        self.name.setGeometry(0,0,width,height)
        icon_width = width // 3
        icon_height = height // 3
        if self.shortcut.icon and not self.icon_pixmap.isNull():
            self.icon.setGeometry(0, 0, icon_width, icon_height)
        if not self.good:
            self.lock.setGeometry(width - icon_width, 0, icon_width, icon_height)
            
            if not self.lock_pixmap.isNull():
                # Scale first
                scaled = self.lock_pixmap.scaled(
                    self.lock.width(), self.lock.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                self.lock.setPixmap(scaled)
                self.lock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        super().resizeEvent(event)
    def mousePressEvent(self, event):
        self.shortcut.run([])
        super().mousePressEvent(event)