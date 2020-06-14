from intersection.junction import Junction
from intersection.world import Edge
from intersection.widgets import Drawer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
import sys

if __name__ == "__main__":
    app = QApplication([])
    drawer = Drawer()
    drawer.setWindowTitle("Area")
    drawer.show()

    e1 = Edge('e1', 'id', 'id2', 10)
    e2 = Edge('e2', 'id', 'id2', 20)
    junction = Junction("id", QRectF(-5, -5, 10, 10))
    junction.addLane("lan1", [QPointF(-5, 0), QPointF(5, 0)], e1, e2)
    junction.addLane("lan2", [QPointF(5, 0), QPointF(-5, 0)], e2, e1)
    drawer.objects.append(junction)
    sys.exit(app.exec_())
