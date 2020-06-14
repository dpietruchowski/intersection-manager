from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math

class Cell(QPoint):
    def __repr__(self):
        return repr('Cell(' + str(self.x()) + ', ' + str(self.y()) + ')')

    def row(self):
        return self.y()
    
    def col(self):
        return self.x()

class Area:
    cellSize = 0.5
    def __init__(self, shape):
        self.shape = QPolygonF(shape)
        self.rect = self.shape.boundingRect()

    def getCellRect(self, cell):
        rect = QRectF(cell.col() * self.cellSize, cell.row() * self.cellSize, self.cellSize, self.cellSize)
        rect.translate(self.rect.x(), self.rect.y())
        return rect

    def min(self):
        return Cell(0, 0)

    def max(self):
        return Cell(self.rect.width()/self.cellSize,
                    self.rect.height()/self.cellSize)

    def range(self):
        return [Cell(j, i) for i in self.rangeRow() for j in self.rangeCol()]
        
    def rangeRow(self):
        return range(self.min().row(), self.max().row())
    
    def rangeCol(self):
        return range(self.min().col(), self.max().col())

    def getCell(self, point):
        point -= self.rect.topLeft()
        x = math.ceil(point.x() / self.cellSize) - 1
        y = math.ceil(point.y() / self.cellSize) - 1
        col = min(max(self.min().col(), x), self.max().col() - 1)
        row = min(max(self.min().row(), y), self.max().row() - 1)
        return Cell(col, row)

    def getCellsOccupied(self, polygon):
        rect = polygon.boundingRect()
        '''if not self.rect.intresects(rect):
            return []'''
        topLeft = self.getCell(rect.topLeft())
        botRight = self.getCell(rect.bottomRight())
        cells = []
        for col in range(topLeft.col(), botRight.col() + 1):
            for row in range(topLeft.row(), botRight.row() + 1):
                cells.append(Cell(col, row))
        return cells

        '''retCells = []
        for cell in cells:
            i = polygon.intersects(polygon)
            if polygon.intersects(QPolygonF(self.getCellRect(cell))):
                cells.append(cell)
        return retCells'''
    
    def draw(self, painter):
        painter.drawRect(self.rect)
        cells = self.range()
        painter.save()
        painter.setOpacity(0.2)
        for cell in cells:
            painter.drawRect(self.getCellRect(cell))
        painter.restore()
        painter.pen().setColor(Qt.blue)
        painter.drawPolygon(self.shape)

class LaneItem:
    pass
    
class Lane:
    distStep = 0.05
    width = 1
    length = 2
    def __init__(self, shape, area, fromEdge, toEdge):
        self.shape = shape
        self.area = area
        self.cellReg = {}
        self.fromEdge = fromEdge
        self.toEdge = toEdge

    def __repr__(self):
        if not self.isConnection():
            return repr('Lane is not connected')
        return repr('Lane|' + str(self.id) + '| ' + self.fromEdge.id + '->' + self.toEdge.id)

    def isConnection(self):
        return  self.fromEdge and self.toEdge

    def recalculate(self):
        self.cellReg = {}
        distance = 0
        currentLineDist = 0
        distNum = 0
        for idx in range(1, len(self.shape)):
            line = QLineF(self.shape[idx - 1], self.shape[idx])
            while distance < currentLineDist + line.length():
                t = (distance - currentLineDist) / line.length()
                polygon = self.getBoundingPolygon(line, t, self.length, self.width)
                self.cellReg[distNum] = self.area.getCellsOccupied(polygon)
                distance += self.distStep
                distNum += 1
            currentLineDist += line.length()

    # 0 < t < 1
    def getBoundingPolygon(self, line, t, length, width):
        length = float(length)
        width = float(width)
        polygon = QPolygonF([QPointF(-length/2, -width/2), QPointF(-length/2, width/2),
                            QPointF(length/2, width/2), QPointF(length/2, -width/2)])
        transform = QTransform().rotate(360 - line.angle())
        polygon = transform.map(polygon)
        p1 = line.pointAt(t)
        polygon.translate(p1.x(), p1.y())
        return polygon

    def getCarPolygon(self, fdist):
        distance = 0
        currentLineDist = 0
        
        for idx in range(1, len(self.shape)):
            line = QLineF(self.shape[idx - 1], self.shape[idx])
            while distance < currentLineDist + line.length():
                if fdist < distance:
                    t = (fdist - currentLineDist) / line.length()
                    return self.getBoundingPolygon(line, t, self.length, self.width)
                distance += self.distStep
            currentLineDist += line.length()
        return None
                

    def getCells(self, distance):
        distance = float(distance)
        idx = int(math.ceil(distance / self.distStep))
        if idx not in self.cellReg:
            return []
        return self.cellReg[idx]

    def draw(self, painter):
        pen = painter.pen()
        pen.setColor(Qt.red)
        painter.setPen(pen)
        for idx in range(1, len(self.shape)):
            line = QLineF(self.shape[idx - 1], self.shape[idx])
            painter.drawLine(line)
        '''for distance in self.cellReg:
            for cell in self.cellReg[distance]:
                painter.fillRect(self.area.getCellRect(cell), Qt.blue)'''

class Junction:
    def __init__(self, id, areaShape):
        self.id = id
        self.area = Area(areaShape)
        self.lanes = {}
        self.manager = None

    def hasManager(self):
        return self.manager is not None
    
    def addLane(self, id, shape, fromEdge, toEdge):
        if id in self.lanes:
            return
        lane = Lane(shape, self.area, fromEdge, toEdge)
        lane.id = id
        self.lanes[id] = lane
        lane.recalculate()

    def getLane(self, fromEdgeId, toEdgeId):
        for id, lane in self.lanes.items():
            if not lane.isConnection():
                continue
            if lane.fromEdge.id == fromEdgeId and lane.toEdge.id == toEdgeId:
                return lane
        return None
        
    def draw(self, painter):
        self.area.draw(painter)
        for id, lane in self.lanes.items():
            lane.draw(painter)


if __name__ == "__main__":
    cell = Cell(0, 0)
    print (cell)
    area = Area(QRectF(-5, -5, 10, 10))
    print area.getCellsOccupied(QPolygonF(QRectF(-5, -5, 5, 5)))