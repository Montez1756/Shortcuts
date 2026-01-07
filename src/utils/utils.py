from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics


def elideText(label, text):
        metrics = QFontMetrics(label.font())
        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, label.width())
        return elidedText

from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt

def tint_pixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.GlobalColor.transparent)  # transparent base

    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, pixmap)  # draw original
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), color)  # apply tint
    painter.end()
    return tinted
