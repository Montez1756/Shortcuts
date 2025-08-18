import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

LPY = 'shorcut/Scripts/python.exe'

class Shortcut(QWidget):
    def __init__(self, parent, info):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.console = parent.console
        #Python File to run
        self.file = info['file']
        #Info about shortcut
        self.info_file = info['info']
        #Location of python in shortcut venv
        self.python = info['python']
        #Info file parsed into json
        self.json = None
        self.loadInfo()
        #Shortcut Icon
        self.icon = None
        self.icon_file = info['icon']
        if self.icon_file:
            self.setIcon(self.icon_file)
        #Shortcut Styles
        self.name = 'Unnamed'
        background_color = None
        if self.json:
            b = self.json.get('background_color')
            background_color = b if b else "#444"
            self.name = self.json.get('name') or 'Unnamed'
            desc = self.json.get('desc') or ''
            self.setToolTip(desc)
        self.initial_style = f"background-color: {background_color}; border-radius: 10px;"
        

        self.label = QLabel(self.name, self)
        self.label.setStyleSheet("color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, 1)
        self.setStyleSheet(self.initial_style)
        self.setAcceptDrops(True)
    def loadInfo(self):
        try:
            with open(self.info_file, 'r') as file:
                try:
                    self.json = json.loads(file.read())
                except:
                    self.json = None
        except:
            return None
    def setIcon(self, src):
        self.icon = QLabel(self)
        self.icon.setStyleSheet("background: transparent;")
        
        pixmap = QPixmap(src)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon.setPixmap(pixmap)
        self.icon.show()
    def mousePressEvent(self, a0):
        if a0.button() == Qt.LeftButton:
            self.run([])
        return super().mousePressEvent(a0)
    def resizeEvent(self, event):
        if self.icon:
            self.icon.setGeometry(15,15,30,30)
            self.icon.raise_()
    def dragEnterEvent(self, a0):
        a0.acceptProposedAction()
        return super().dragEnterEvent(a0)
    def dragMoveEvent(self, a0):
        a0.acceptProposedAction()
        return super().dragMoveEvent(a0)
    def dragLeaveEvent(self, a0):
        return super().dragLeaveEvent(a0)
    def dropEvent(self, a0):
        if a0.mimeData().hasUrls():
            urls = [u.toLocalFile() for u in a0.mimeData().urls()]
            self.run(urls)
        return super().dropEvent(a0)
    def run(self, *args):
        exe = self.python or LPY
        self.console.run(exe, self.file, *args)