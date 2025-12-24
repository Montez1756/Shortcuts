import os
from PyQt5.QtWidgets import QWidget
from src.core.shortcuts import Shortcut
class ShortcutManager:
    def __init__(self, shortcuts_dir : str, parent : QWidget = None):
        print(parent)
        self.parent = parent
        self.shortcuts_dir = shortcuts_dir

        self.shortcuts : list[Shortcut] = []
        self.initShortcuts()
    def initShortcuts(self):
        for path in os.listdir(self.shortcuts_dir):
            ""
            self.shortcuts.append(Shortcut(os.path.join(self.shortcuts_dir, path), self.parent))
    def getShortcuts(self) -> list[Shortcut]:
        return self.shortcuts
    def reload(self):
        for shortcut in self.shortcuts:
            shortcut.delete()
            shortcut.deleteLater()
        
        self.initShortcuts()