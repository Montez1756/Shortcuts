import os, subprocess, sys, json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QSizePolicy, QPushButton, QStyle, QSystemTrayIcon, QMenu, QAction,
                              QCheckBox, QTextEdit)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QSize, QRect, QMimeData, QTimer, QProcess, QUrl, QEvent
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QImage, QWheelEvent
from shortcut import Shortcut
from console import Console
from configparser import ConfigParser
from automation import Automator


def get_shortcuts():
    shortcut_dir = os.path.join(os.getcwd(), 'shortcuts')
    shortcuts = []
    for d in os.listdir('shortcuts'):
        d = os.path.join(shortcut_dir, d)
        if os.path.isdir(d):
            paths = [
                {
                    'name':'file',
                    'path':'file/(any)'
                },
                {
                    'name':'icon',
                    'path':'icon/(any)'
                },
                {
                    'name':'info',
                    'path':'info.json'
                },
                {
                    'name':'python',
                    'path':['venv/Scripts/python.exe', 'venv/bin/python']
                }
                ]
            shortcut_info = {}
            if os.path.exists(os.path.join(d, '.auto')):
                continue
            for path in paths:
                if path['name'] == 'python'
                if '(any)' in path['path']:
                    sub = os.path.join(d, path['name'])
                    if os.path.exists(sub):
                        path['path'] = path['path'].replace('(any)', os.listdir(sub)[0])
                file_path = os.path.join(d, path['path'])
                if os.path.exists(file_path):
                    shortcut_info[path['name']] = file_path
                else:
                    shortcut_info[path['name']] = ''
            # shortcut_info['file'] = os.path.join(d, 'main.py')
            # shortcut_info['icon'] = os.path.join(d, 'icon.jpg')
            # shortcut_info['info'] = os.path.join(d, 'info.json')
            # python_exe = os.path.join(d, 'venv', 'Scripts', 'python.exe')
            # if not os.path.exists(python_exe):
            #     python_exe = None
            # shortcut_info['python'] = python_exe
            shortcuts.append(shortcut_info)
    
    return shortcuts
def get_automations():
    shortcut_dir = os.path.join(os.getcwd(), 'shortcuts')
    shortcuts = []
    for d in os.listdir('shortcuts'):
        d = os.path.join(shortcut_dir, d)
        if os.path.isdir(d):
            paths = [
                {
                    'name':'file',
                    'path':'file/(any)'
                },
                {
                    'name':'icon',
                    'path':'icon/(any)'
                },
                {
                    'name':'info',
                    'path':'info.json'
                },
                {
                    'name':'python',
                    'path':'venv/Scripts/python.exe'
                }
                ]
            shortcut_info = {}
            auto_file = os.path.join(d, '.auto')
            if os.path.exists(auto_file):
                attrs = subprocess.check_output(['attrib', auto_file]).decode().strip()
                flags, path = attrs.rsplit(' ', 1)
                if 'H' not in flags:
                    subprocess.run(['attrib', '+h', auto_file])
                for path in paths:
                    if '(any)' in path['path']:
                        sub = os.path.join(d, path['name'])
                        if os.path.exists(sub):
                            path['path'] = path['path'].replace('(any)', os.listdir(sub)[0])
                    file_path = os.path.join(d, path['path'])
                    if os.path.exists(file_path):
                        shortcut_info[path['name']] = file_path
                    else:
                        shortcut_info[path['name']] = ''
                shortcuts.append(shortcut_info)
            else:
                continue
    return shortcuts
class TitleBar(QWidget):
    def __init__(self, app: QApplication, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(f'background-color: {parent.backgroundColor}; border-bottom: 1px solid #222;')
        
        self._parent = parent
        self._app = app
        self._is_maximized = False

        self.icon_label = QLabel(self)
        self.icon_label.setStyleSheet("background-color:transparent;")
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        pixmap = QPixmap(r'shortcuts.png')
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setGeometry(5, 3, 24, 24)  # Adjust as needed

        self.title_label = QLabel("Shortcuts", self)
        self.title_label.setStyleSheet("color: white; font-weight: bold; background-color:transparent;")
        self.title_label.setGeometry(35, 0, 200, self.height())  # Adjust width
            

        self.button_w = 30
        self.button_h = 30  # You should define a height for buttons

        # Store parent and app references

        # Create buttons using standard icons
        style = self._app.style()

        self.minimize = QPushButton(style.standardIcon(QStyle.SP_TitleBarMinButton), '', self)
        self.minimize.clicked.connect(self.minimize_window)

        self.maximize = QPushButton(style.standardIcon(QStyle.SP_TitleBarMaxButton), '', self)
        self.maximize.clicked.connect(self.toggle_maximize_restore)

        self.quit = QPushButton(style.standardIcon(QStyle.SP_TitleBarCloseButton), '', self)
        self.quit.clicked.connect(self._parent.close)  # use close(), not quit

        for btn in (self.minimize, self.maximize, self.quit):
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #333;
                }
            """)

        # Manually call resize handler to set button positions
        self.resizeEvent(None)
        parent.installEventFilter(self)
        
    def resizeEvent(self, event):
        """ Update button positions when resized """
        w = self._parent.width()
        h = self.button_h
        self.setFixedSize(w,h)
        for index, button in enumerate([self.quit, self.maximize, self.minimize]):
            button.setGeometry(w - (index + 1) * self.button_w, 0, self.button_w, h)
        # self.minimize.setGeometry(w - 3 * self.button_w, 0, self.button_w, h)
        # self.maximize.setGeometry(w - 2 * self.button_w, 0, self.button_w, h)
        # self.quit.setGeometry(w - 1 * self.button_w, 0, self.button_w, h)

    def toggle_maximize_restore(self):
        if self._is_maximized:
            self._parent.showNormal()
            self.maximize.setIcon(self._app.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        else:
            self._parent.showMaximized()
            self.maximize.setIcon(self._app.style().standardIcon(QStyle.SP_TitleBarNormalButton))
        self._is_maximized = not self._is_maximized

    def minimize_window(self):
        self._parent.hide()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self._parent.move(self._parent.pos() + event.globalPos() - self._drag_pos)
            self._drag_pos = event.globalPos()
    def eventFilter(self, obj, event):
        if obj == self._parent and event.type() == event.Resize:
            self.resizeEvent(event)
        return super().eventFilter(obj, event)   

class MainWindow(QWidget):
    def __init__(self, app = QApplication):
        super().__init__()
        self.app = app
        config = ConfigParser()
        config.read('options.ini')
        if 'Window' in config:
            self._width = int(config['Window'].get('Width')) or 500
            self._height = int(config['Window'].get('Height')) or 500
            self.backgroundColor = config['Window'].get('BackgroundColor') or 'Black'
            self.minOnStart = {'true':True, 'false':False}.get(config['Window'].get('MinOnStart').lower()) or False 
            
        self.setWindowTitle("Shortcuts")
        self.setGeometry(0, 0, self._width, self._height)
        self.setWindowIcon(QIcon(QPixmap('shortcuts.png')))
        self.setStyleSheet(f'background-color:{self.backgroundColor};')
        self._y = 0

        self.console = Console(self, app)
        self.console.setGeometry(0, 40, self.width(), self.height())

        self.shortcuts = [Shortcut(self, info) for info in get_shortcuts()]
        self.automations = [Shortcut(self, info) for info in get_automations()]

        self.titleBar = TitleBar(app, self)
        self.titleBar.raise_()
        self.titleBar.setGeometry(0 , 0, self.width(), 40)


        self.reload_button = QPushButton(app.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload), '', self)
        self.reload_button.setStyleSheet("background-color:transparent;")
        self.reload_button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.reload_button.clicked.connect(self.reload)
        self.reload_button.setGeometry(0, self.height() - 30, 30,30)


        self.automator = Automator(self.automations,self)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.show)
        show_action = QAction('Show', self)
        quit_action = QAction('Quit', self)
        hide_action = QAction('Hide', self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit)
        hide_action.triggered.connect(self.hide)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.setWindowFlag(Qt.FramelessWindowHint)
        if not self.minOnStart:
            self.show()
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        inc = 15
        if delta > 0:
            self._y = min(0, self._y + inc)
        elif delta < 0:
            self._y = min(0, self._y - inc)
        self.resizeEvent(None)
        return super().wheelEvent(event)
    def resizeEvent(self, event):
        padding = 10  # space between each shortcut
        cols = 3
        item_w = (self.width() - padding * (cols + 1)) // cols
        item_h = (self.height() - padding * (cols + 1)) // cols  # rows = cols here if you want square grid
        self.reload_button.setGeometry(0,self.height() - 30, 30, 30)
        for i, shortcut in enumerate(self.shortcuts + self.automations):
            row = i // cols
            col = i % cols
            x = padding + col * (item_w + padding)
            y = padding + row * (item_h + padding) + self.titleBar.height() + self._y
            shortcut.setGeometry(QRect(x, y, item_w, item_h))
    def reload(self):
    # Remove existing shortcuts
        for s in self.shortcuts:
            s.hide()
            s.setParent(None)
            s.deleteLater()

        # Recreate shortcuts
        self.shortcuts = [Shortcut(self, info) for info in get_shortcuts()]
        self.automations = [Shortcut(self, info) for info in get_automations()]
        self.automator.automations = self.automations
        self.automator.reload()
        # Show the new shortcuts
        for s in self.shortcuts:
            s.show()

        # Manually trigger layout by calling resizeEvent
        self.resizeEvent(None)
    def hideShortcuts(self):
        for shortcut in self.shortcuts:
            shortcut.setVisible(False)
            shortcut.setDisabled(True)
    def showShortcuts(self):
        for shortcut in self.shortcuts:
            shortcut.setVisible(True)
            shortcut.setDisabled(False)
    def quit(self):
        self.tray_icon.hide()
        self.app.quit()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    sys.exit(app.exec())
