from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QFont, QFontDatabase
from enum import IntFlag


class InputType(IntFlag):
    Text = 0x00000000
    Int = 0x00000001
    File = 0x00000002
class InputDialog(QWidget):
    Accepted = 1
    Rejected = 0
    def __init__(self, parent : QWidget = None, label : str = "", placeholder : str = "", mask : str = "", yn : bool = False):
        super().__init__(parent)
        self._parent = parent
        self.label = label
        self.placeholder = placeholder
        self.input_mask = mask
        self.res = 0
        self.yn = yn
        self.text_w = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("border-radius:10px;")
        self.initGui()
    def initGui(self):
        self.label_w = QLabel(self.label, self)
        self.label_w.setFont(QFont("Arial", 12))

        if not self.yn:
            self.text_w = QLineEdit(self)
            self.text_w.setPlaceholderText(self.placeholder)
            self.text_w.setStyleSheet("border-radius:10px; background-color:rgba(255,255,255,0.2); padding:5;")
            self.text_w.setFont(QFont("Arial", 12))
            self.text_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if self.input_mask:
                self.text_w.setInputMask(self.input_mask)

        self.ok_b = QPushButton("Ok", self)
        self.ok_b.clicked.connect(self.accept)
        
        self.cancel_b = QPushButton("Cancel", self)
        self.cancel_b.clicked.connect(self.reject)
    def resizeEvent(self, a0):
        p_width = self._parent.width()
        p_height = self._parent.height()

        padding = 65

        width = p_width - padding
        height = p_height - padding

        self.setGeometry(p_width // 2 - (width // 2), p_height // 2 - (height // 2), width, height)
        
        self.label_w.adjustSize()
        self.label_w.move(width // 2 - (self.label_w.width() // 2), 5)        


        if self.text_w:
            text_width = width - 10
            text_height = height // 5
            
            self.text_w.setGeometry(width // 2 - (text_width // 2), height // 2 - (text_height // 2), width - 10, height // 5)
        
        button_w = width // 4
        button_h = height // 4

        self.ok_b.setGeometry(width - (button_w * 2), height - (button_h + 10), button_w, button_h)
        self.cancel_b.setGeometry(width - (button_w * 1), height - (button_h + 10), button_w, button_h)

    def mousePressEvent(self, a0):
        super().mousePressEvent(a0)
        a0.accept()
    def exec_(self):
        self.loop = QEventLoop()
        self.loop.exec_()

        return self.res
    def accept(self):
        self.res = InputDialog.Accepted
        if self.loop:
            self.loop.quit()
        self.close()
    def reject(self):
        self.res =  InputDialog.Rejected
        if self.loop:
            self.loop.quit()
        self.close()
    def text(self):
        return self.text_w.text()