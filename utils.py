from PyQt5.QtWidgets import QWidget, QFileDialog, QLineEdit
from PyQt5.QtCore import QObject, Qt


class DictForm(QWidget):

    def __init__(self, keys : dict = [], parent : QWidget = None):
        super().__init__(parent)
        self.keys = [QLineEdit(self) for key in keys]
        for key in self.keys:
            key.setStyleSheet("padding:10px;")
            key.adjustSize()
    def resizeEvent(self, a0):
        padding = 10

        y = 0
        for key in self.keys:
            key.setGeometry(0, y, 50, 20)
            y += 20 + padding 
        super().resizeEvent(a0)

class ShortcutCreator(QWidget):
    def __init__(self, parent : QWidget = None):
        super().__init__(parent)
        self.setGeometry(0,0,500,500)
        self.creation_list = [
            {
                "name":"file",
                "path":"file/",
                "type":self.strInput
            },
            {
                "name":"info",
                "path":"info.json",
                "type":self.dictInput,
                "keys":["name", "desc", "background_color"]
            },
            {
                "name":"icon",
                "path":"icon/",
                "type":self.fileInput
            },

        ] 
        self.inputs = []
        self.load_list()
        self.show()
    def strInput(self):
        return QLineEdit(self)
    def dictInput(self, keys):
        return DictForm(keys, self)
    def fileInput(self):
        return self.strInput()
    def load_list(self):
        for input in self.creation_list:
            if input["type"] == self.dictInput:
                self.inputs.append(input["type"](input["keys"]))
                continue
            self.inputs.append(input["type"]())
    def resizeEvent(self, a0):
        width = self.width()
        height = self.height()

        y = 0
        input_h = int(height // 10)
        padding = 10
        for input in self.inputs:
            half_width = width // 2
            input.setGeometry(half_width - (half_width // 2), y, half_width, input_h)
            y += input_h + padding
        super().resizeEvent(a0)