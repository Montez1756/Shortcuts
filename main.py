from PyQt5.QtWidgets import QApplication
import sys
from window import MainWindow


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.aboutToQuit.connect(window.quit)
    # creator = ShortcutCreator(None)
    sys.exit(app.exec_())




