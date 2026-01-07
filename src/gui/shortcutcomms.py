from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QApplication
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer
from input import InputDialog
from media import DynamMedia
from .menu import Menu
import json


class Comms(QWidget):
    return_signal = pyqtSignal(str)
    def __init__(self, parent : QWidget = None):
        super().__init__(parent)
        self.h_layout = QHBoxLayout(self)
        self.setLayout(self.h_layout)
class CommsPrompt(Comms):
    def __init__(self, msg : dict, parent : QWidget = None):
        super().__init__(parent)
        try:
            print(msg["prompt"])
            self.msg : dict = msg.get("prompt")
        except json.JSONDecodeError as error:
            print(error)
        self.prompt()
    def prompt(self):

        label = self.msg.get("label", "Prompt")
        placeholder = self.msg.get("placeholder")
        input_mask = self.msg.get("mask")

        self.dlg = InputDialog(self, label, placeholder, input_mask)
        self.dlg.show()
        res = self.dlg.exec_()
        if res == InputDialog.Accepted:
            self.return_signal.emit(self.dlg.text())

class CommsMessage(Comms):
    def __init__(self, msg: dict, parent = None):
        super().__init__(parent)

        self.msg = msg.get("message")
        self.message()
    def message(self):
        self.msg_d = QTextEdit(self.msg, self)
        self.msg_d.setStyleSheet("background-color:rgb(25,25,25); color:white;")
        self.msg_d.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_d.setReadOnly(True)
        self.msg_d.setVisible(True)
        self.h_layout.addWidget(self.msg_d)

class CommsDisplay(Comms):
    def __init__(self, msg : dict, parent : QWidget = None):
        super().__init__(parent)

        self.msg = msg.get("display")
        self.display()
    def display(self):
        self.media_d = DynamMedia(self.msg, self)
    def resizeEvent(self, a0):
        self.media_d.resize(self.width(), self.height())
        self.media_d.raise_()
        return super().resizeEvent(a0)
class CommsMenu(Comms):
    def __init__(self, msg : dict, parent : QWidget = None):
        super().__init__(parent)
        try:
            self.msg = msg.get("menu")
        except json.JSONDecodeError as error:
            print(error)
        
    def menu(self):
        self.menu_d = Menu(self.msg, self)
        self.menu_d.clicked_signal.connect(self.return_signal.emit)
        self.h_layout.addWidget(self.menu_d)

class ShortcutComms(QWidget):
    def __init__(self, parent : QWidget = None):
        super().__init__(parent)
        self.h_layout = QHBoxLayout(self)
        self.msg_queue : list[str] = []
        self.comms : Comms = None
    def handleMsg(self, msg : str) -> tuple:
        if self.comms:
            self.msg_queue.append(msg)
            return
        msg = json.loads(msg)
        
        msg_dict = {
            "message":CommsMessage,
            "prompt":CommsPrompt,
            "display":CommsDisplay,
            "menu":CommsMenu
        }
        
        for key in msg_dict.keys():
            if key in msg:
                comms = msg_dict[key](msg, self)
                self.h_layout.addWidget(comms)
                comms.raise_()
                timer = QTimer(self)
                timer.singleShot(1500, comms.deleteLater)
                break
    # def finished(self):
    #     if self.comms:
    #         self.comms.setVisible(False)
    #         self.comms.deleteLater()
    #         self.comms = None