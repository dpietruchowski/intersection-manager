from intersection.junction import Cell
from intersection.manager import Manager, CellRegister

import unittest

class TestManager(unittest.TestCase):
    def testCellRegister(self):
        reg = CellRegister()
        reg.register(0, Cell(0,0), 'car1')
        reg.register(0, Cell(1,1), 'car2')
        reg.register(0, Cell(2,2), 'car2')
        reg.register(0, Cell(3,3), 'car2')
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


    def testManager(self):
        manager = Manager()

    
if __name__ == "__main__":
    unittest.main(exit=True)