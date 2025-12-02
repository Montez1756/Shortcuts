from PyQt5.QtWidgets import (QWidget, QFileDialog, QLineEdit, QLabel, QPushButton,
                              QCheckBox, QGraphicsBlurEffect, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import QObject, Qt, QRectF
from PyQt5.QtGui import QFontMetrics, QPainterPath, QRegion
import os, json


def elideText(label, text):
        metrics = QFontMetrics(label.font())
        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, label.width())
        return elidedText

class Form(QWidget):
    def __init__(self, name, parent):
        super().__init__(parent)
        self._parent = parent
        self.name = name

        self.name_label = QLabel(self.name, self)

    def setValue(self, value):
        raise NotImplementedError
    def getValue(self):
        raise NotImplementedError
    def resizeEvent(self, a0):
        width = self.width()
        height = self.height()

        self.name_label.setGeometry(0,0, width, height // 10)

class StrForm(Form):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.text = QLineEdit(self)

    def setValue(self, value):
        self.text.setText(value)
    def getValue(self):
        return self.text.text()
    def resizeEvent(self, a0):
        width = self.width()
        height = self.height()

        self.text.setGeometry(width // 20, (height // 10) + 5, width - width // 20, height // 10)
        return super().resizeEvent(a0)
class DictForm(Form):
    def __init__(self, keys, name, parent):
        super().__init__(name, parent)
        self.keys = keys
        self.key_cls = []
        layout = QVBoxLayout(self)
        for key in keys:
            k = StrForm(key, self)
            layout.addWidget(k)
            self.key_cls.append(k)
        self.setLayout(layout)
    def setValue(self, value : dict):
        # for key in value.keys():
        ""
    def getValue(self, value):
        temp = {}
        for cls in self.key_cls:
            name = getattr(cls, "name", "None")
            value = cls.getValue()
            temp[name] = value
        return temp
    # def resizeEvent(self, a0):
    #     width = self.width()
    #     height = self.height()
    #     for cls in self.key_cls:
    #         cls.setGeometry(width // 20, (height // 10) + 5, width - width // 20, height // 10)

    #     return super().resizeEvent(a0)
class FileForm(Form):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        layout = QVBoxLayout(self)

        self.file_button = QPushButton("Select File", self)
        self.file = ""
        self.file_label = QLabel(self.file, self)

        layout.addWidget(self.file_button, 0)
        layout.addWidget(self.file_label, 0)

        self.setLayout(layout)
    def getValue(self):
        return self.file
    # def resizeEvent(self, a0):
        

    #     return super().resizeEvent(a0)
class BoolForm(Form):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        layout = QVBoxLayout()

        self.check_box = QCheckBox(self)
        layout.addWidget(self.check_box)

        self.setLayout(layout)

class ShortcutCreator(QWidget):
    def __init__(self, shortcut : QWidget = None, parent : QWidget = None):
        super().__init__(parent)
        self._parent = parent
        
        self.setStyleSheet("background-color:rgb(24,24,24);")

        self.shortcut = shortcut
        self.creation_list = [

            {
                "name":"shortcut",
                "path":"shortcut/",
                "type":StrForm,
                "path_type":"base"
            },
            {
                "name":"file",
                "path":"file/",
                "type":StrForm,
                "path_type":"directory"
            },
            {
                "name":"info",
                "path":"info.json",
                "type":DictForm,
                "keys":["name", "desc", "background_color"],
                "path_type":"file"
            },
            {
                "name":"icon",
                "path":"icon/",
                "type":FileForm,
                "path_type":"directory"
            },
            {
                "name":"auto",
                "path":".auto",
                "type":BoolForm,
                "path_type":"file"
            }
        ] 
        
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.setObjectName("shortcut-button")
        # self.confirm_button.clicked.connect(self.saveForms)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.hide)
        self.cancel_button.setObjectName("shortcut-button")
        
        self.setStyleSheet(self.styleSheet() + "#shortcut-button{border-radius:10px; color:lightgrey;}")

        # for button in [self.confirm_button, self.cancel_button]:

        self.inputs = {}
        
        self.load_forms()
        
        # self.show()
        self.setVisible(False)
    def load_forms(self):
        layout = QVBoxLayout(self)
        
        
        for creation in self.creation_list:
            if creation["name"] != "info":
                layout.addWidget(creation["type"](creation["name"], self))
            else:
                layout.addWidget(creation["type"](creation["keys"], creation["name"], self))