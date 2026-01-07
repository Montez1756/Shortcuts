from PyQt5.QtWidgets import QApplication, QCommonStyle
import sys
from src.gui.window import MainWindow


if __name__ == "__main__":
    print("Creating APP")
    app = QApplication([])
    app.setStyleSheet("*{background-color:rgb(100,100,100);color:lightgrey;}")
    window = MainWindow()
    app.aboutToQuit.connect(window.quit)
    sys.exit(app.exec_())
    print("Exiting APP")
5