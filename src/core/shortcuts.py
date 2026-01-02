import os, shutil
from PyQt5.QtCore import QObject, pyqtSignal,QProcess, pyqtSlot
from PyQt5.QtWidgets import QWidget
from src.utils.config import getShortcutConfig
from .shortcutproccess import ShortcutProccess
from ..gui.shortcut_gui import ShortcutGui

class Shortcut(QObject):
    def __init__(self, path, parent : QWidget = None):
        super().__init__(None)
        self._parent = parent
        self.auto = False
        self.good = False
        self.gui = None
        self.path = path
        self.process = None
        self.info_dict = getShortcutConfig(self.path)

        self.init()
    def init(self):
        if os.path.exists(self.path):
            self.good = True if self.info_dict.get("file") else False
            self.gui = ShortcutGui(self.info_dict, self.good, self._parent)
            self.gui.run_signal.connect(self.run)
            self.gui.delete_signal.connect(self.delete)
    def get(self, name):
        return self.info_dict.get(name)
    def getGui(self):
        return self.gui
    def run(self, args):
        if self.good:
            exe = self.info_dict.get("venv")
            file = self.info_dict.get("file")
            cwd = self.info_dict.get("cwd")

            self.process = ShortcutProccess(exe, [file] + args, cwd)

            self.process.stdipc.connect(self.gui.handleMsg)
            # self.process.stdipc.connect(print)
            # self.process.stdout.connect(print)
            # self.process.stderr.connect(print)
            self.process.finished.connect(self.process.deleteLater)

            self.process.start()
    def delete(self):
            self._parent.deleteShortcut(self.gui)
            shutil.rmtree(self.path)
            self.deleteLater()

