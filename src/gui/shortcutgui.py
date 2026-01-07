from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTextEdit, QApplication, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QProcess
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from ..utils.utils import tint_pixmap
from .shortcutcomms import ShortcutComms
from gui.input import InputDialog
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
        
        self.initgui()

        self.comms = ShortcutComms(self)
        self.comms.raise_()


        self.setAcceptDrops(True)
        self.setVisible(True)
    """
    
    Custom Logic
    
    """
    def initgui(self):
        self.icon = QLabel(self)

        if self.info.get("icon"):
            self.icon_pixmap = QPixmap(self.info.get("icon"))
            if not self.icon_pixmap.isNull():
                self.icon.setPixmap(self.icon_pixmap.scaled((self.width() // 4), (self.height() // 4), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        if not self.good:
            self.lock_pixmap = QPixmap('resources/lock.png')
            self.lock_pixmap = tint_pixmap(self.lock_pixmap, QColor(200, 0, 0))
            if not self.lock_pixmap.isNull():
                self.lock = QLabel(self)
                self.lock.setStyleSheet("background-color:transparent;")
                self.lock.setPixmap(self.lock_pixmap)


        self.name = QLabel(self.info.get("name", "Unnamed").capitalize(), self)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Ariel", 15,5,False)
        self.name.setFont(font)

        self.cancelButton = QPushButton(QIcon("resources/close.png"), "", self)
        self.cancelButton.clicked.connect(self.stop_signal.emit)

        self.editButton = QPushButton(QIcon("resources/edit.png"), "", self)
        self.editButton.clicked.connect(lambda:print("Displaying edit menu...")) #Improve shortcut creator in general and to load shortcuts and make this display it

        self.deleteButton = QPushButton(QIcon("resources/delete.png"), "", self)
        self.deleteButton.clicked.connect(self.delete)
        
        # #create container widget for buttons and use layout to organize
        self.cancelButton.setObjectName("button")
        self.editButton.setObjectName("button")
        self.deleteButton.setObjectName("button")


        self.cancelButton.setVisible(False)
        self.editButton.setVisible(False)
        self.deleteButton.setVisible(False)

    def run(self, args : list = []) -> None:
        self.cancelButton.setVisible(True)
        self.run_signal.emit(args)
    #Clean up process guis stuff
    def finished(self):
        @pyqtSlot()
        def clean():
            self.cancelButton.setVisible(False)
            # self.comms.finished()
        timer = QTimer(self)
        timer.singleShot(1500, clean)
        # print("Program Finished")
    def handleMsg(self, msg : str):
        self.comms.handleMsg(msg)
        self.cancelButton.raise_()
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

        name_width = width // 2
        name_height = width // 2

        self.name.setGeometry((width // 2) - name_width // 2, (height // 2) - name_height // 2, name_width, name_height)

        buttons = [self.cancelButton, self.editButton, self.deleteButton]

        button_width = width // 8
        button_height = height // len(buttons)

        for i, button in enumerate(buttons):
            button.setGeometry(width - (button_width + 10), (button_height * i) + 10, button_width, button_height)

        self.comms.setGeometry(0,0, width, height)

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
