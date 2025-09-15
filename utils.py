from PyQt5.QtWidgets import QWidget, QFileDialog, QLineEdit, QLabel, QPushButton, QCheckBox
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QFontMetrics
import os, json

def createFile(path, mode, need_file):
    file = open(path, mode)
    if need_file:
        return file
    else:
        file.close()

def elideText(label, text):
        metrics = QFontMetrics(label.font())
        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, label.width())
        return elidedText

class Form(QWidget):
    def __init__(self, name : str = "", parent : QWidget = None):
        super().__init__(parent)
        self.name = name
        self.name_label = QLabel(name, self)
        self.name_label.setText(elideText(self.name_label, self.name_label.text().capitalize()))
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
            key.setGeometry(padding, y, width - padding, key_height)
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
        self.percent = 8
        self.str = QLineEdit(self)
        self.str.setContentsMargins(0,0,0,0)
        self.placeholder = placeholder
        if placeholder:
            self.name_label.setVisible(False)

        self.str.setPlaceholderText(name.capitalize())
    def resizeEvent(self, a0):
        width = self.width()
        height = self.height()
        if not self.placeholder:
            height //= 2
            self.name_label.setGeometry(0,0, (width // 4), height)
            margin = int(self.name_label.width() // 1.5)
            self.str.setGeometry(0, height, width, height)
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
        self.file_label.setGeometry(10, height, width - 10, height)
        return super().resizeEvent(a0)
    def promptFile(self):
        file = QFileDialog().getOpenFileName(self, "Select File", filter="Image Files (*.png *.jpg *.bmp)")
        if len(file):
            self.file = file[0]
            self.file_label.setText(elideText(self.file_label, self.file))
    def getValue(self):
        return self.file
    
class boolForm(Form):
    def __init__(self, name = "", parent = None):
        super().__init__(name, parent)
        self.percent = 10
        self.check_button = QCheckBox(self)
        self.value = False
        self.check_button.clicked.connect(self.clicked)

    def clicked(self):
        self.value = False if self.value else True
        self.check_button.setText(str(self.value))

    def resizeEvent(self, a0):
        width = self.width()
        height = self.height() // 2

        self.name_label.setGeometry(0, 0, width, height)

        self.check_button.setGeometry(10, height, width // 3, height)
    def getValue(self):
        return self.value
class ShortcutCreator(QWidget):
    def __init__(self, parent : QWidget = None):
        super().__init__(parent)
        self.setStyleSheet("background-color:rgb(24,24,24); color:lightgrey; border-color:lightgrey;")
        self.widget = QWidget(self)

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
            {
                "name":"auto",
                "path":".auto",
                "type":self.boolInput
            }
        ] 
        
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.clicked.connect(self.saveForms)
        
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.hide)
        
        self.inputs = {}
        
        self.load_list()
        
        # self.show()
        self.setVisible(False)

    def strInput(self):
        return StrForm
    def dictInput(self):
        return DictForm
    def fileInput(self):
        return FileForm
    def boolInput(self):
        return boolForm
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

        self.widget.setGeometry(0,0, width, height)

        button_width = width // 4
        button_height = height // 12
        self.confirm_button.setGeometry((width // 2), (height - (button_height + 10)), button_width, button_height)
        self.cancel_button.setGeometry(((width // 2) + (button_width)), (height - (button_height + 10)), button_width, button_height)

        y = 0
        padding = 10
        for key in self.inputs.keys():
            input = self.inputs[key]
            input_h = int(height // input.percent)
            half_width = width // 2
            input.setGeometry(half_width - (half_width // 2), y, half_width, input_h)
            y += input_h + padding
        super().resizeEvent(a0)
    def saveForms(self):
        shortcut = ""
        for creation in self.creation_list:
            name = creation["name"]
            path  = creation["path"]
            _input = self.inputs[name]
            value = _input.getValue()
            if value:
                if name == "shortcut":
                    shortcut = os.path.join(path, value)
                    os.makedirs(shortcut, exist_ok=True)
                elif name == "file":
                    file = os.path.join(shortcut, path, value)
                    os.makedirs(os.path.join(shortcut, "file"), exist_ok=True)
                    createFile(file, "w+", False)
                elif name == "info":
                    file = os.path.join(shortcut, path)
                    file = createFile(file, "w+", True)
                    _json = value
                    file.write(json.dumps(_json))
                    file.close()
                elif name == "icon":
                    os.makedirs(os.path.join(shortcut, "icon"), exist_ok=True)
                    _value = os.path.basename(value)
                    file = os.path.join(shortcut, path, _value)
                    file = createFile(file, "wb+", True)
                    with open(value, "rb") as icon_file:
                        file.write(icon_file.read())
                    file.close()
                elif name == "auto":
                    if value:
                        createFile(os.path.join(shortcut, ".auto"), "w+", False)

"LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab"