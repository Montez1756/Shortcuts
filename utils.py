from PyQt5.QtWidgets import QWidget, QFileDialog, QLineEdit, QLabel, QPushButton
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QFontMetrics
import os, json

def createFile(path, need_file):
    file = open(path, "wb+")
    if need_file:
        return file
    else:
        file.close()

class Form(QWidget):
    def __init__(self, name : str = "", parent : QWidget = None):
        super().__init__(parent)
        self.name = name
        self.name_label = QLabel(name, self)
        self.name_label.setText(self.name_label.text().capitalize())
        self.value = None
        # self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.percent = 3
    def getValue(self):
        raise NotImplementedError
class DictForm(Form):

    def __init__(self, name : str = "", keys : dict = [], parent : QWidget = None):
        super().__init__(name, parent)
        # self.setStyleSheet("background-color:black;")
        # self.widget = QWidget(self)

        self.keys = [StrForm(key, True, self) for key in keys]
        
        # self.keys = [QLineEdit(self) for key in keys]
    def resizeEvent(self, a0):
        width = self.width()
        height = self.height()

        self.name_label.adjustSize()
        self.name_label.move(0,0)
        
        keys_len = len(self.keys)
        padding = 10
        height -= (keys_len * padding) + self.name_label.height() 
        
        y = self.name_label.height()
        key_height = int(height // len(self.keys))
        for key in self.keys:
            key.setGeometry(0, y, width, key_height)
            y += key_height + padding
        super().resizeEvent(a0)
    def getValue(self):
        temp = {}
        for key in self.keys:
            temp[key.name] = key.getValue()
        return temp
class StrForm(Form):
    def __init__(self, name : str = "", placeholder : bool = False, parent : QWidget = None):
        super().__init__(name, parent)
        self.percent = 12
        self.str = QLineEdit(self)
        self.str.setContentsMargins(0,0,0,0)
        if placeholder:
            self.name_label.setVisible(False)
            self.str.setPlaceholderText(name.capitalize())
    def resizeEvent(self, a0):
        width = self.width()
        height = self.height()
        if not self.placeholder:
            self.name_label.setGeometry(0,0, (width // 4), height)
            margin = int(self.name_label.width() // 1.5)
            self.str.setGeometry(margin, 0, (width - margin), height)
        else:
            self.str.setGeometry(0,0, width, height)
        super().resizeEvent(a0)
    def getValue(self):
        return self.str.text()
class FileForm(Form):
    def __init__(self, name: str = "", parent: QWidget = None):
        super().__init__(name, parent)
        self.percent = 10
        self.file_button = QPushButton("File", self)
        self.file_button.clicked.connect(self.promptFile)
        self.file = "None"
        self.file_label = QLabel("None", self)

    def resizeEvent(self, a0):
        width = self.width()
        height = self.height() // 2


        self.name_label.setGeometry(0,0, (width // 4), height)
        margin = int(self.name_label.width() // 1.5)
        self.file_button.setGeometry(margin, 0, (width - margin), height)
        self.file_label.setGeometry(0, height, width, height)
        return super().resizeEvent(a0)
    def promptFile(self):
        file = QFileDialog().getOpenFileName(self, "Select File", filter="Image Files (*.png *.jpg *.bmp)")
        if len(file):
            self.file = file[0]
            self.file_label.setText(self.elideText(self.file_label, self.file))
    def elideText(self, label, text):
        metrics = QFontMetrics(label.font())
        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, label.width())
        return elidedText
    def getValue(self):
        return self.file
class ShortcutCreator(QWidget):
    def __init__(self, parent : QWidget = None):
        super().__init__(parent)
        self.setGeometry(0,0,500,500)
        self.creation_list = [
            {
                "name":"shortcut",
                "path":"shortcut/",
                "type":self.strInput
            },
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
        return StrForm
    def dictInput(self):
        return DictForm
    def fileInput(self):
        return FileForm
    def load_list(self):
        for input in self.creation_list:
            input_cls = input["type"]()
            if input["type"] == self.dictInput:
                self.inputs[input["name"]] = input_cls(input["name"], input["keys"], self)
                continue
            if input["type"] == self.strInput:
                self.inputs[input["name"]] = input_cls(input["name"], False, self)
            else:
                self.inputs[input["name"]] = input_cls(input["name"], self)
    def resizeEvent(self, a0):
        width = self.width()
        height = self.height()

        y = 0
        padding = 10
        for input in self.inputs:
            input_h = int(height // input.percent)
            half_width = width // 2
            input.setGeometry(half_width - (half_width // 2), y, half_width, input_h)
            y += input_h + padding
        super().resizeEvent(a0)
    def saveForms(self):
        shortcut = ""
        for creation in self.creation_list:
            name = creation.name
            path  = creation.path
            _input = self.inputs[name]
            value = _input.getValue()
            if value:
                if name == "shortcut":
                    shortcut = os.path.join(path, value)
                    os.mkdir(shortcut)
                elif name == "file":
                    file = os.path.join(shortcut, path, value)
                    createFile(file)
                elif name == "info":
                    file = os.path.join(shortcut, path)
                    file = createFile(file, True)
                    _json = value
                    file.write(json.dumps(_json))
                    file.close()
                elif name == "icon":
                    _value = os.path.basename(value)
                    file = os.path.join(shortcut, path, _value)
                    file = createFile(file, True)
                    with open(value, "rb") as icon_file:
                        file.write(icon_file.read())
                    file.close()

"LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab"