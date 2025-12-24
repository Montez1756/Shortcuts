from PyQt5.QtWidgets import QSystemTrayIcon, QWidget, QAction, QMenu, QApplication

class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent : QWidget = None):
        super().__init__(icon, parent)

        menu = QMenu(None)
        show = QAction("Show", menu)
        show.triggered.connect(parent.show)
        
        hide = QAction("Hide", menu)
        hide.triggered.connect(parent.hide)
        
        quit = QAction("Quit", menu)
        quit.triggered.connect(QApplication.quit)

        menu.addActions([show, hide, quit])
        self.setContextMenu(menu)