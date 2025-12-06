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
        self.setStyleSheet("QWidget{background-color:rgb(50,50,50);border-radius:10px;}")
        self.closeButton = QPushButton(QIcon("resources/close.png"), "", self)
        # self.closeButton.
        self.closeButton.clicked.connect(self.close)
        self.resizeEvent(None)
    def resizeEvent(self, a0):
        p_width = self._parent.width()
        p_height = self._parent.height()

        self.label.adjustSize()

        padding = 100
        width = self.label.width() + padding
        height = self.label.height() + padding
        self.label.resize(width, height)
        self.closeButton.setGeometry(width - 30, 0, 30, 30)
        x = p_width // 2 - (width // 2)
        y = p_height // 2 - (height // 2)
        self.setGeometry(x, y, width, height)
        
        self.raise_()
