from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QGraphicsScene, QGraphicsView, QSizePolicy
from PyQt5.QtCore import QUrl, Qt, QRectF, QSizeF
from PyQt5.QtGui import QPixmap, QPainterPath, QRegion
import os

video_extensions = [
    ".mp4", ".mov", ".avi", ".wmv", ".flv", ".mkv", ".webm", ".avchd", ".mts", ".m2ts",
    ".ts", ".3gp", ".3g2", ".mpg", ".mpeg", ".vob", ".ogv", ".ogg", ".gifv", ".m4v",
    ".rm", ".asf", ".amv", ".f4v", ".f4p", ".f4a", ".f4b", ".mod"
]

image_extensions = [
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".ico",
    ".heic", ".heif", ".psd", ".raw", ".arw", ".cr2", ".nef", ".dng", ".orf", ".sr2",
    ".pict", ".jp2", ".jpx", ".j2k", ".jpf", ".jpm", ".jxs", ".jxr", ".hdr", ".exr"
]

class DynamMedia(QWidget):
    def __init__(self, source : str, parent : QWidget = None):
        super().__init__(parent)
        self.type = None

        root, ext = os.path.splitext(source)

        if video_extensions.count(ext):
            self.type = "video"
        elif image_extensions.count(ext):
            self.type = "image"
        else:
            self.type = "text"

        self.source = source
        self.main_widget : QWidget = None
        self.pixmap = None

        if self.type == "video":
            self.video()
        elif self.type == "image":
            self.image()
        else:
            self.text()

        if self.main_widget:
            self.main_widget.setVisible(True)
            self.main_widget.setStyleSheet("border-radius:10px; background-color:rgb(25,25,25);")
            self.main_widget.raise_()
        self.resizeEvent(None)
        self.show()
    def video(self):
        self.main_widget = QGraphicsView(self)
        self.main_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        self.scene = QGraphicsScene(self)
        self.main_widget.setScene(self.scene)
        
        self.video_item = QGraphicsVideoItem()
        self.video_item.setAspectRatioMode(Qt.AspectRatioMode.IgnoreAspectRatio)
        self.scene.addItem(self.video_item)

        player = QMediaPlayer(self)
        player.setVideoOutput(self.video_item)
        player.setMedia(QMediaContent(QUrl.fromLocalFile(self.source)))
        player.play()

        # self.player = QMediaPlayer(self)

        # self.main_widget = QVideoWidget(self)
        # self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.source)))
        # self.player.setVideoOutput(self.main_widget)

        # self.player.play()
    def image(self):
        self.main_widget = QLabel(self)
        self.pixmap = QPixmap(self.source)
        if not self.pixmap.isNull():
            self.main_widget.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.main_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    def text(self):
        self.main_widget = QTextEdit(self)
        self.main_widget.setReadOnly(True)
        self.main_widget.setTextColor(Qt.GlobalColor.white)
        with open(self.source, "r") as file:
            self.main_widget.setText(file.read())
    def resizeEvent(self, a0):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)


        width = self.width()
        height = self.height()

        if self.main_widget:
            self.main_widget.setGeometry(0,0,width,height)
        if getattr(self, "video_item", None):
            self.video_item.setSize(QSizeF(self.size()))
        if self.pixmap:
            pixmap = self.pixmap.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.main_widget.setPixmap(pixmap)
