import os, json, sys, shutil
from PyQt5.QtCore import (QObject, Qt, pyqtSignal, QRectF, QUrl, QProcess, QThread,
                           pyqtSlot, QTimer, QRectF)
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QInputDialog, QTextEdit,
                              QApplication, QMenu, QAction, QPushButton, QMessageBox)
from PyQt5.QtGui import QPixmap, QColor, QFont, QFontDatabase, QPainterPath, QRegion, QIcon
from gui import tint_pixmap
from media import DynamMedia
from Error import Error
import glob
MM = '{EMC}'

class ShortcutWorker(QObject):
    output_signal = pyqtSignal()
    error_signal = pyqtSignal()
    finished_signal = pyqtSignal()
    force_finish_signal = pyqtSignal()
    prompt_signal = pyqtSignal(str)
    def __init__(self, shortcut, args):
        super().__init__(shortcut)
        self.shortcut = shortcut
        self.args = args
        self.process = None
    def run(self):
        exe = self.shortcut.get("exe")
        file = self.shortcut.get("file")
        dir_name = getattr(self.shortcut, "path")
        self.process = QProcess(self)
        self.process.setWorkingDirectory(dir_name)
        self.process.readyReadStandardOutput.connect(self.output_signal.emit)
        self.process.readyReadStandardError.connect(self.error_signal.emit)
        self.process.finished.connect(self.finished_signal.emit)
        self.force_finish_signal.connect(self.process.kill)
        self.process.start(exe, [file] + self.args)
    @pyqtSlot(str)
    def write(self, value : str):
        self.process.write(bytes((value + '\n').encode('utf-8')))
        self.process.waitForBytesWritten()
    def kill(self):
        self.process.kill()
class Shortcut(QObject):
    def __init__(self, path, parent : QWidget = None):
        super().__init__(None)
        self._parent = parent
        self.auto = False
        self.good = False
        self.gui = None
        self.path = path
        self.process = None

        self.init()
    def init(self):
        error = 0
        if os.path.exists(self.path):
            self.info_dict = dict()
            info_file = os.path.join(self.path, "info.json")
            if os.path.exists(info_file):
                with open(info_file, "r") as file:
                    try:
                        self.info_dict = json.loads(file.read())
                    except json.JSONDecodeError as e:
                        self.info_dict["name"] = "[!]Error[!]"
                        Error(f"Error: Failed to parse info.json file in shortcut path: {info_file}", self._parent)
                        error = 1
            shortcut_dict = dict()
            # for key in ["name", "disc", "background_color", "icon"]:
            #     info_v = self.info_dict.get(key)
            #     if info_v:
            #         shortcut_dict[key] = info_v

            paths = [
            {"name": "file",       "path": "file/*.py"},
            {"name": "exe",        "path": ["venv/Scripts/python.exe", "venv/bin/python"]},
            {"name": "icon",       "path": "icon/*"},
            {"name": "automation", "path": ".auto"},
            ]

            for path in paths:
                path_n = path["name"]
                path_p = path["path"]
                if isinstance(path_p, str):
                        print(path_n)
                        path_temp = glob.glob(os.path.join(self.path, path_p))
                        if path_temp and os.path.exists(path_temp[0]):
                            self.info_dict[path_n] = path_temp[0]
                if isinstance(path_p, list):
                    for path_s in path_p:
                        path_temp = os.path.join(self.path, path_s)
                        if os.path.exists(path_temp):
                            self.info_dict[path_n] = path_temp
                    if not self.info_dict.get(path_n):
                        self.info_dict[path_n] = sys.executable
            
            shortcut_dict.update(self.info_dict)
            self.good = True if self.info_dict.get("file") and not error else False
            self.gui = ShortcutGui(shortcut_dict, self.good, self._parent)
            self.gui.run_signal.connect(self.run)
            self.gui.delete_signal.connect(self.delete)
    def get(self, name):
        return self.info_dict.get(name)
    def getGui(self):
        return self.gui
    def run(self, args):
        if self.good:
            
            self._thread = QThread(self)
            worker = ShortcutWorker(self, args)
            worker.moveToThread(self._thread)

            worker.output_signal.connect(lambda: self.handleOutput(worker))
            self.gui.write_signal.connect(worker.write)
            worker.error_signal.connect(lambda: self.handleError(worker.process))

            worker.finished_signal.connect(self._thread.quit)
            worker.finished_signal.connect(worker.deleteLater)
            worker.finished_signal.connect(self.gui.finished)

            self.gui.stop_signal.connect(worker.kill)

            self._thread.started.connect(worker.run)
            self._thread.finished.connect(self._thread.deleteLater)
            self._thread.start()
            print("good and running")
        else:
            print("not good")    
    def handleOutput(self, worker):
        process = worker.process
        if process:
            output = bytes(process.readAllStandardOutput()).decode("utf-8", errors="ignore").strip()
            for line in output.splitlines():
                if line.startswith(MM):
                    self.gui.handleMsg(line.split(MM, 1)[1], process)
    def handleError(self, process):
        output = bytes(process.readAllStandardError()).decode("utf-8", errors="ignore").strip()
        for line in output.splitlines():
            print(line)
    def delete(self):
        confirmBox = QMessageBox(self._parent)
        confirmBox.setWindowTitle("Are you sure?")
        confirmBox.setText("Are you sure you want to delete this shortcut?")
        confirmBox.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok)
        confirmBox.setDefaultButton(QMessageBox.StandardButton.Ok)
        confirmBox.setWindowFlags(Qt.FramelessWindowHint)
        confirmBox.setStyleSheet("background-color:rgb(50,50,50);color:lightgrey; border-radius:10px; padding:10;")
        for button in confirmBox.buttons():
            text = button.text()
            if text == "&OK":
                button.setStyleSheet("color:green;")
            else:
                button.setStyleSheet("color:red;")
        res = confirmBox.exec()
        if res == QMessageBox.StandardButton.Ok:
            self._parent.deleteShortcut(self.gui)
            shutil.rmtree(self.path)
            self.deleteLater()

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
        self._style = self._style = "#main{{background-color:{0}; border-radius:10px;}} QLabel{{background-color:transparent; color:lightgrey;}} #button{{background-color:transparent;}}"
        
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
        self.deleteButton.clicked.connect(self.delete_signal.emit)
        
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
    """
    
    Custom Logic
    
    """

    def run(self, args : list = []) -> None:
        self.cancelButton.setVisible(True)
        self.run_signal.emit(args)
    def handleMsg(self, msg : str, process : QProcess) -> tuple:
        msg = json.loads(msg)
        print(msg)
        a = {}
        key = list(msg.keys())[0]
        value = msg[key]
        def prompt(placeholder):
            dlg = QInputDialog(self, Qt.WindowType.FramelessWindowHint)
            dlg.setLabelText(placeholder.capitalize())
            dlg.setInputMode(QInputDialog.TextInput)

            if dlg.exec_() == QInputDialog.Accepted:
                text = dlg.textValue()
                self.write_signal.emit(text)
            else:
                self.finished()
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
