from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class Error(QWidget):
    def __init__(self, msg, parent : QWidget = None):
        super().__init__(parent)
        self._parent = parent
        self.msg = msg
        self.label = QLabel(msg, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("QWidget{background-color:rgb(50,50,50);color:lightgrey;border-radius:10px;}")
        self.closeButton = QPushButton(QIcon("resources/close.png"), "", self)
        # self.closeButton.
        self.closeButton.setStyleSheet("color:white;")
        self.closeButton.clicked.connect(self.close)
        self.resizeEvent(None)
    def resizeEvent(self, a0):
        x = self._parent.width() // 4
        y = self._parent.height() // 4

        self.label.adjustSize()
        # self.label.resize(width, height)
        padding = 100
        width = self.label.width() + padding
        height = self.label.height() + padding
        self.label.resize(width, height)
        self.closeButton.setGeometry(width - 30, 0, 30, 30)
        print(width, height)
        self.setGeometry(x, y, width, height)
        
        self.raise_()
