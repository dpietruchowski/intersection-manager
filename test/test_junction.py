from intersection.junction import Cell, Lane, Area
from intersection.world import Edge
from PyQt5.QtCore import *

import unittest

class TestJunction(unittest.TestCase):
    def testLane(self):
        area = Area(QRectF(-5, -5, 10, 10))
        e1 = Edge('e1', None, None, 10)
        e2 = Edge('e2', None, None, 20)
        lane1 = Lane([QPointF(-5, 0), QPointF(5, 0)], area, e1, e2)
        lane1.recalculate()

    
if __name__ == "__main__":
    unittest.main(exit=True)