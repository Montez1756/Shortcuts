import os, json
from PyQt5.QtCore import QObject, QProcess, Qt
from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor, QPixmap, QIcon, QPalette
MM = '{EMC}'


class ConsoleGui(QWidget):
    def __init__(self, parent : QWidget = None):
        super().__init__(parent)
        self._parent = parent
        
        self.setStyleSheet("background-color:rgb(24,24,24);")

        self.widget = QWidget(self)

        icon = QIcon('src/close.png')
        self.closeButton = QPushButton(icon, '', self)
        self.closeButton.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.closeButton.setStyleSheet("background-color:transparent;")
        self.closeButton.clicked.connect(self.finished)

        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.text.setTextColor(QColor.fromRgb(255,255,255))
        self.text.setStyleSheet("background-color:transparent; border:none;")
        # layout.addWidget(self.text)

        self.setVisible(False)
    def append(self, text): 
        self.text.append(text)
    def resizeEvent(self, event):
        width = self.width()
        height = self.height()

        self.widget.setGeometry(0,0, width, height)
        self.closeButton.setGeometry(width - 50, 0, 50, 50)
        self.closeButton.raise_()

        self.text.setGeometry(0,50, width, height - 50)

        super().resizeEvent(event)
    def finished(self):
        self.setVisible(False)
        self.text.clear()
        
class Console(QObject):
    def __init__(self, gui : ConsoleGui = None):
        super().__init__(None)
        self.gui = gui
    def run(self, shortcut, args):
        exe = shortcut.exe
        file = shortcut.file
        dir_name = shortcut.dir_name
        self.gui.setVisible(True)
        self.gui.raise_()
        self.append(f"Running Command -> {exe} {file} {args}")
        self.process = QProcess(self)
        self.process.setWorkingDirectory(dir_name)

        self.process.readyReadStandardOutput.connect(self.handleOutput)
        self.process.readyReadStandardError.connect(self.handleError)
        self.process.finished.connect(lambda exitCode: self.append(self.colorText(f"Script Finished: {exitCode}", "green")))
        
        if file.endswith(".py"):
            self.process.start(exe, [file] + args)
        elif file.endswith(".bat"):
            self.process.start("cmd", ['/c', file] + args)
    def handleOutput(self):
            output = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="ignore").strip()
            for line in output.splitlines():
                if line.startswith(MM):
                    self.handleMessage(line[len(MM):])
                else:
                    self.append(line)
    def handleMessage(self, text):
        try:
            j = json.loads(text)
            for key in j.keys():
                    self.append(self.colorText(j[key], "green"))
        except Exception as e:
            self.appendError(str(e))
    def handleError(self):
        output = bytes(self.process.readAllStandardError()).decode('utf-8', errors="ignore").strip()
        for line in output.splitlines():
            self.appendError(line)
    def append(self, text):
        self.gui.append(text)
    def colorText(self, text, color):
        return f'<span style="color:{color};">{text}</span>'
    def appendError(self, text):
        error = self.colorText(text, 'red')
        self.gui.append(error)

