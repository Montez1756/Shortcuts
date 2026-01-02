from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QPainterPath, QRegion
import json
class Menu(QWidget):
    clicked_signal = pyqtSignal(str)
    def __init__(self, menu_dict : dict, parent : QWidget = None):
        super().__init__(parent)
        self.dict = menu_dict
        self.options : list[QPushButton] = []
        self.setAttribute(Qt.WA_TranslucentBackground)
        if not isinstance(self.dict, dict) and isinstance(self.dict, str):
            try:
                self.dict = json.loads(self.dict)
            except Exception as e:
                print(f"Json Exception: {e}")

        for key, value in self.dict.items():
            option = QPushButton(key, self)
            option.clicked.connect(lambda checked=False, v=value: self.clicked_signal.emit(v))
            # option.setStyleSheet("background-color:rgb(25,25,25); color:lightgrey; border:none;")
            option.setStyleSheet("""
                QPushButton {
                    background-color: rgba(25, 25, 25, 0.9);
                    color: lightgrey;
                    border: none;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(50, 50, 50, 0.9);
                }
            """)
            self.options.append(option)

    def resizeEvent(self, a0):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        
        # Layout the buttons
        width = self.width()
        height = self.height() // max(len(self.options), 1)
        y = 0
        for option in self.options:
            option.setGeometry(0, y, width, height)
            y += height
