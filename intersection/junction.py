from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math, logging

class Cell(QPoint):
    def __repr__(self):
        return repr('Cell(' + str(self.x()) + ', ' + str(self.y()) + ')')

    def row(self):
        return self.y()
    
    def col(self):
        return self.x()

class Area:
    cell_size = 0.5
    def __init__(self, shape):
        self.shape = QPolygonF(shape)
        self.rect = self.shape.boundingRect()

    def get_cellRect(self, cell):
        rect = QRectF(cell.col() * self.cell_size, cell.row() * self.cell_size, self.cell_size, self.cell_size)
        rect.translate(self.rect.x(), self.rect.y())
        return rect

    def min(self):
        return Cell(0, 0)

    def max(self):
        return Cell(self.rect.width()/self.cell_size,
                    self.rect.height()/self.cell_size)

    def range(self):
        return [Cell(j, i) for i in self.range_row() for j in self.range_col()]
        
    def range_row(self):
        return range(self.min().row(), self.max().row())
    
    def range_col(self):
        return range(self.min().col(), self.max().col())

    def get_cell(self, point):
        point -= self.rect.topLeft()
        x = math.ceil(point.x() / self.cell_size) - 1
        y = math.ceil(point.y() / self.cell_size) - 1
        col = min(max(self.min().col(), x), self.max().col() - 1)
        row = min(max(self.min().row(), y), self.max().row() - 1)
        return Cell(col, row)

    def get_cells_occupied(self, polygon):
        rect = polygon.boundingRect()
        '''if not self.rect.intresects(rect):
            return []'''
        topLeft = self.get_cell(rect.topLeft())
        botRight = self.get_cell(rect.bottomRight())
        cells = []
        for col in range(topLeft.col(), botRight.col() + 1):
            for row in range(topLeft.row(), botRight.row() + 1):
                cells.append(Cell(col, row))
        return cells

        '''retCells = []
        for cell in cells:
            i = polygon.intersects(polygon)
            if polygon.intersects(QPolygonF(self.get_cellRect(cell))):
                cells.append(cell)
        return retCells'''
    
    def draw(self, painter):
        painter.drawRect(self.rect)
        cells = self.range()
        painter.save()
        painter.setOpacity(0.2)
        for cell in cells:
            painter.drawRect(self.get_cellRect(cell))
        painter.restore()
        painter.pen().setColor(Qt.blue)
        painter.drawPolygon(self.shape)

class LaneItem:
    pass
    
class Lane:
    dist_step = 0.05
    car_width = 1
    car_length = 2
    def __init__(self, shape, area, length, from_edge, to_edge):
        self.shape = shape
        self.area = area
        self.length = length
        self.cell_reg = {}
        self.from_edge = from_edge
        self.to_edge = to_edge

    def __repr__(self):
        if not self.is_connection():
            return repr('Lane is not connected')
        return repr('Lane|' + str(self.id) + '| ' + self.from_edge.id + '->' + self.to_edge.id)

    def is_connection(self):
        return  self.from_edge and self.to_edge

    def recalculate(self):
        self.cell_reg = {}
        distance = 0
        current_line_dist = 0
        dist_num = 0
        for idx in range(1, len(self.shape)):
            line = QLineF(self.shape[idx - 1], self.shape[idx])
            while distance < current_line_dist + line.length():
                t = (distance - current_line_dist) / line.length()
                polygon = self.get_bounding_polygon(line, t, self.car_length, self.car_width)
                self.cell_reg[dist_num] = self.area.get_cells_occupied(polygon)
                distance += self.dist_step
                dist_num += 1
            current_line_dist += line.length()
        if self.length != current_line_dist:
            logging.warning("Lane length doesn't match")

    # 0 < t < 1
    def get_bounding_polygon(self, line, t, length, width):
        length = float(length)
        width = float(width)
        polygon = QPolygonF([QPointF(-length/2, -width/2), QPointF(-length/2, width/2),
                            QPointF(length/2, width/2), QPointF(length/2, -width/2)])
        transform = QTransform().rotate(360 - line.angle())
        polygon = transform.map(polygon)
        p1 = line.pointAt(t)
        polygon.translate(p1.x(), p1.y())
        return polygon

    def get_car_polygon(self, fdist):
        distance = 0
        current_line_dist = 0
        
        for idx in range(1, len(self.shape)):
            line = QLineF(self.shape[idx - 1], self.shape[idx])
            while distance < current_line_dist + line.length():
                if fdist < distance:
                    t = (fdist - current_line_dist) / line.length()
                    return self.get_bounding_polygon(line, t, self.car_length, self.car_width)
                distance += self.dist_step
            current_line_dist += line.length()
        return None
                

    def get_cells(self, distance):
        idx = int(math.floor(float(distance) / self.dist_step))
        if idx not in self.cell_reg:
            return []
        return self.cell_reg[idx]

    def draw(self, painter):
        pen = painter.pen()
        pen.setColor(Qt.red)
        painter.setPen(pen)
        for idx in range(1, len(self.shape)):
            line = QLineF(self.shape[idx - 1], self.shape[idx])
            painter.drawLine(line)
        '''for distance in self.cell_reg:
            for cell in self.cell_reg[distance]:
                painter.fillRect(self.area.get_cellRect(cell), Qt.blue)'''

class Junction:
    def __init__(self, id, areaShape):
        self.id = id
        self.area = Area(areaShape)
        self.lanes = {}
        self.manager = None

    def has_manager(self):
        return self.manager is not None
    
    def add_lane(self, id, shape, length, from_edge, to_edge):
        if id in self.lanes:
            return
        lane = Lane(shape, self.area, length, from_edge, to_edge)
        lane.id = id
        self.lanes[id] = lane
        lane.recalculate()

    def get_lane(self, from_edge_id, to_edge_id):
        for id, lane in self.lanes.items():
            if not lane.is_connection():
                continue
            if lane.from_edge.id == from_edge_id and lane.to_edge.id == to_edge_id:
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
    print area.get_cells_occupied(QPolygonF(QRectF(-5, -5, 5, 5)))