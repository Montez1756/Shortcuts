from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTextEdit, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QProcess
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from ..utils.utils import tint_pixmap
from .menu import Menu
from media import DynamMedia
from input import InputDialog
import json
class ShortcutGui(QWidget):
    run_signal = pyqtSignal(list) # Signal for telling shortcut class it should run the shortcut
    write_signal = pyqtSignal(str) # Signal to send input data back to shortcut to write to shortcut process
    stop_signal = pyqtSignal() # Signal to tell shortcut class to force stop shortcut process
    delete_signal = pyqtSignal() # Signal to tell shortcut class that shortcut is going to be deleted for proper cleanup
    def __init__(self, info = dict, good = bool, parent : QWidget = None):
        super().__init__(parent)

        self._parent = parent
        self.setObjectName("parent")
        self.good = good
        self.info = info
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setObjectName("main")
        self.initial_color = info.get("background_color", "rgb(75,75,75)")
        self._style = self._style = "#main{{background-color:{0}; border-radius:10px;}} QLabel{{background-color:transparent; color:lightgrey;}} #button{{background-color:transparent;}} QDialog{{border-radius:10px;}}"
        
        self.setStyleSheet(self._style.format(self.initial_color))    
        self.setContentsMargins(10,10,10,10)
        
        self.name = QLabel(self.info.get("name", "Unnamed").capitalize(), self)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Ariel", 12,10,False)
        self.name.setFont(font)

        self.cancelButton = QPushButton(QIcon("resources/close.png"), "", self)
        self.cancelButton.clicked.connect(self.stop_signal.emit)

        self.editButton = QPushButton(QIcon("resources/edit.png"), "", self)
        self.editButton.clicked.connect(lambda:print("Displaying edit menu...")) #Improve shortcut creator in general and to load shortcuts and make this display it

        self.deleteButton = QPushButton(QIcon("resources/delete.png"), "", self)
        self.deleteButton.clicked.connect(self.delete)
        
        #create container widget for buttons and use layout to organize
        self.cancelButton.setObjectName("button")
        self.editButton.setObjectName("button")
        self.deleteButton.setObjectName("button")
        self.cancelButton.setVisible(False)
        self.editButton.setVisible(False)
        self.deleteButton.setVisible(False)

        if self.info.get("icon"):
            self.icon_pixmap = QPixmap(self.info.get("icon"))
            if not self.icon_pixmap.isNull():
                self.icon = QLabel(self)
                self.icon.setPixmap(self.icon_pixmap)
        if not self.good:
            self.lock_pixmap = QPixmap('resources/lock.png')
            self.lock_pixmap = tint_pixmap(self.lock_pixmap, QColor(200, 0, 0))
            if not self.lock_pixmap.isNull():
                self.lock = QLabel(self)
                self.lock.setStyleSheet("background-color:transparent;")
                self.lock.setPixmap(self.lock_pixmap)

        self.message_d : QTextEdit = None
        self.media_d : DynamMedia = None
        self._menu : Menu = None
        self.setAcceptDrops(True)
        self.setVisible(True)
        self.dlg = None
    """
    
    Custom Logic
    
    """

    def run(self, args : list = []) -> None:
        self.cancelButton.setVisible(True)
        self.run_signal.emit(args)
    #Clean up process guis stuff
    def finished(self):
        @pyqtSlot()
        def clean():
            self.cancelButton.setVisible(False)
            if self.message_d:
                self.message_d.setVisible(False)
                self.message_d.deleteLater()
                self.message_d = None
                # print("Cleaned")
            if self.media_d:
                self.media_d.setVisible(False)
                self.media_d.deleteLater()
                self.media_d = None
            if self._menu:
                self._menu.setVisible(False)
                self._menu.deleteLater()
                self._menu = None
        timer = QTimer(self)
        timer.singleShot(1500, clean)
        # print("Program Finished")
    def handleMsg(self, msg : str) -> tuple:
        msg = json.loads(msg)
        key = list(msg.keys())[0]
        value = msg[key]
        def prompt(prompt_ob : dict) -> None:
            label = prompt_ob.get("label")
            placeholder = prompt_ob.get("placeholder")
            input_mask = prompt_ob.get("mask")
            self.dlg = InputDialog(self, label, placeholder, input_mask)
            self.dlg.show()
            res = self.dlg.exec_()
            if res == InputDialog.Accepted:
                self.write_signal.emit(self.dlg.text())
            else:
                self.finished()
            # dlg = QInputDialog(self)
            # dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
            # dlg.setLabelText(placeholder.capitalize())
            # dlg.setInputMode(QInputDialog.TextInput)
            # dlg.setStyleSheet("border-radius:10px;")

            # dlg.setModal(True)
            # if dlg.exec_() == QInputDialog.Accepted:
            #     text = dlg.textValue()
            #     self.write_signal.emit(text)
            # else:
            #     self.finished()
            # text, ok = QInputDialog.getText(self._parent, "Input", placeholder.capitalize(), flags=Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
            # if ok:
            #     self.write_signal.emit(text)
            # else:
            #     self.finished()
        def message(msg : str) -> None:
            if self.media_d:
                self.media_d.setVisible(False)
                self.media_d.deleteLater()
                self.media_d = None
            self.media_d = QTextEdit(msg, self)
            self.media_d.setStyleSheet("background-color:rgb(25,25,25);")
            self.media_d.setTextColor(Qt.GlobalColor.white)
            self.media_d.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.media_d.setReadOnly(True)
            self.media_d.setVisible(True)
        def display(src : str) -> None:
            if self.media_d:
                self.media_d.setVisible(False)
                self.media_d.deleteLater()
                self.media_d = None
            self.media_d = DynamMedia(src, self)
            self.media_d.setGeometry(0,0,self.width(), self.height())
            print(f"Displaying source {src}")

        def menu(menu_dict : dict) -> None:
            if not isinstance(menu_dict, dict) and isinstance(menu_dict, str):
                try:
                    menu_dict = json.loads(menu_dict)
                except Exception as e:
                    self.finished()
                    print(f"Invalid menu_dict JSON: {e}")
                    return
            window = QApplication.activeWindow() or QWidget()

            width = window.width()
            height = window.height()

            self._menu = Menu(menu_dict, window)
            self._menu.clicked_signal.connect(self.write_signal.emit)
            self._menu.setGeometry(width // 4, 15, width // 2, height // 3)
            self._menu.show()
        msg_dict = {
            "message":message,
            "prompt":prompt,
            "display":display,
            "menu":menu
        }
        result = (key, msg_dict[key](value))
        self.resizeEvent(None)
        return result
    def delete(self):
        self.del_dlg = InputDialog(self, "Are you sure you want to delete this shortcut", "", "", True)
        self.del_dlg.show()
        res = self.del_dlg.exec_()
        if res == InputDialog.Accepted:
            self.delete_signal.emit()
            

    """"
    
    EVENTS
    
    """
    
    def dropEvent(self, a0):
        if a0.mimeData().hasUrls():
            urls = a0.mimeData().urls()
            for i, url in enumerate(urls):
                url_str = url.toString()
                if "file:///" in url_str:
                    urls[i] = url.toLocalFile()
                else:
                    urls[i] = url.toString()
            self.run(urls)
        else:
            print("no urls found")
    def dragEnterEvent(self, a0):
        if a0.mimeData().hasUrls():
            a0.acceptProposedAction()
        else:
            a0.ignore()
    def resizeEvent(self, event):
        width = self.width()
        height = self.height()
        self.name.adjustSize()
        self.name.move(int(width // 2 - self.name.width() // 2), int(height // 2 - self.name.height() // 2))
        self.cancelButton.setGeometry(width - 50, 0, 50,50)
        icon_width = width // 4
        icon_height = height // 4
        if self.info.get("icon") and not self.icon_pixmap.isNull():
            self.icon.setGeometry(5, 5, icon_width, icon_height)
            scaled = self.icon_pixmap.scaled(icon_width, 
                                            icon_height,
                                            Qt.AspectRatioMode.IgnoreAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation
                                            )
            self.icon.setPixmap(scaled)
        if not self.good:
            self.lock.setGeometry((width - icon_width) - 5, 5, icon_width, icon_height)
            
            if not self.lock_pixmap.isNull():
                # Scale first
                scaled = self.lock_pixmap.scaled(
                    self.lock.width(), self.lock.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                self.lock.setPixmap(scaled)
                self.lock.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i, button in enumerate([self.editButton, self.deleteButton]):
            button_width = 50
            button_height = button_width
            button.setGeometry(width - 50, button_height * (i + 1), 50, 50)

        media_width = width - 50
        if self.message_d:
            self.message_d.setGeometry(5,5, media_width, height - 10)
        if self.media_d:
            self.media_d.setGeometry(5,5, media_width, height - 10)
        super().resizeEvent(event)
    def mousePressEvent(self, event):
        self.run([])
        super().mousePressEvent(event)
    def enterEvent(self, a0):
        palette = self.palette()
        background_color = palette.color(self.backgroundRole())
        r, g, b, a = background_color.getRgb()

        # Darken the color, making sure values stay within 0-255
        r = max(r - 30, 0)
        g = max(g - 30, 0)
        b = max(b - 30, 0)

        self.setStyleSheet(self._style.format(f"rgb({r},{g},{b})"))

        self.editButton.setVisible(True)
        self.deleteButton.setVisible(True)
            
        super().enterEvent(a0)
    def leaveEvent(self, a0):
        self.setStyleSheet(self._style.format(self.initial_color))
        self.editButton.setVisible(False)
        self.deleteButton.setVisible(False)
        super().leaveEvent(a0)
