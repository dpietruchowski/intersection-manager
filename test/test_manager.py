from intersection.junction import Cell, Area, Lane
from intersection.manager import Manager, CellRegister
from intersection.world import Edge
from PyQt5.QtCore import *

import unittest

class TestManager(unittest.TestCase):
    def testCellRegister(self):
        reg = CellRegister()
        reg.register(0, Cell(0,0), 'car1')
        reg.register(0, Cell(1,1), 'car2')
        reg.register(0, Cell(2,2), 'car2')
        reg.register(0, Cell(3,3), 'car2')
        reg.register(5, Cell(3,3), 'car2')
        self.assertEqual(reg.getId(0, Cell(0,0)), 'car1')
        self.assertEqual(reg.getId(0, Cell(1,1)), 'car2')
        self.assertEqual(reg.getId(0, Cell(2,2)), 'car2')
        self.assertEqual(reg.getId(0, Cell(3,3)), 'car2')
        self.assertEqual(reg.getAllCells(0),
            [Cell(0,0), Cell(1,1), Cell(2,2), Cell(3,3)])
        self.assertEqual(reg.getAllCells(0, 'car1'),
            [Cell(0,0)])
        self.assertEqual(reg.getAllCells(0, 'car2'),
            [Cell(1,1), Cell(2,2), Cell(3,3)])


    def testCellUnregister(self):
        reg = CellRegister()
        reg.register(0, Cell(0,0), 'car1')
        reg.register(0, Cell(1,1), 'car2')
        reg.register(0, Cell(2,2), 'car2')
        reg.register(0, Cell(3,3), 'car2')
        reg.unregisterAll('car1')
        self.assertEqual(reg.getId(0, Cell(0,0)), None)
        self.assertEqual(reg.getId(0, Cell(1,1)), 'car2')
        self.assertEqual(reg.getAllCells(0),
            [Cell(1,1), Cell(2,2), Cell(3,3)])
        self.assertEqual(reg.getAllCells(0, 'car1'),
            [])


    def testManager(self):
        area = Area(QRectF(-5, -5, 10, 10))
        e1 = Edge('e1', None, None, 10)
        e2 = Edge('e2', None, None, 20)
        lane1 = Lane([QPointF(-5, 0), QPointF(5, 0)], area, 10, None, None)
        lane1.recalculate()
        manager = Manager()
        manager.register(lane1, 'car1', 0, 10)
        self.assertEqual(manager.cars['car1'],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        manager.unregister('car1')
        self.assertFalse('car1' in manager.cars)
        self.assertEqual(manager.cellReg.getAllCells(0, 'car1'),
            [])
        self.assertEqual(manager.cellReg.getAllCells(1, 'car1'),
            [])

        manager.register(lane1, 'car1', 0, 3)
        self.assertEqual(manager.cars['car1'],
            [0, 1, 2])
        manager.register(lane1, 'car1', 4, 10)
        self.assertEqual(manager.cars['car1'],
            [4, 5, 6, 7, 8, 9])

    
if __name__ == "__main__":
    unittest.main(exit=True)