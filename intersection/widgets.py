from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Drawer(QWidget):
    objects = []

    def drawPolygon(self, polygon):
        self.polygons.append(polygon)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.save()
        pen = QPen()
        pen.setWidthF(0.1)
        painter.setPen(pen)
        transform = QTransform().translate(event.rect().width()/2, 
                                           event.rect().height()/2).scale(20, -20)
        painter.setTransform(transform)
        self.drawCenter(painter)
        for obj in self.objects:
            painter.save()
            obj.draw(painter)
            painter.restore()
        painter.restore()
        painter.end()

    def drawCenter(self, painter):
        painter.save()
        center = QRectF(0, 0, 0.05, 0.05)
        pen = QPen(Qt.red)
        painter.setPen(pen)
        painter.drawEllipse(center)
        painter.restore()