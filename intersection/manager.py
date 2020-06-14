from junction import Cell

class Item:
    def __repr__(self):
        return repr('Item|' + str(self.cell) +', ' + str(self.id) + '|')

class CellRegister:
    def __init__(self):
        self.reg = {}

    def register(self, time, cell, id):
        item = self.findCell(time, cell)
        if not item:
            item = Item()
            item.cell = cell
            item.id = id
            if time not in self.reg:
                self.reg[time] = [item]
            else:
                self.reg[time].append(item)
        
            
    def getId(self, time, cell):
        item = self.findCell(time, cell)
        if item:
            return item.id
        return None

    def getAllCells(self, time, id = None):
        cells = []
        if time in self.reg:
            for item in self.reg[time]:
                if id and item.id == id:
                    cells.append(item.cell)
                elif not id:
                    cells.append(item.cell)
        return cells

    def findCell(self, time, cell):
        if time in self.reg:
            for item in self.reg[time]:
                if item.cell == cell:
                    return item
        return None

class Manager:
    def __init__(self):
        self.cellReg = CellRegister()
        self.cars = {}

    def registerCar(self, carId, laneId, time, velocity):
        if laneId not in self.lanes:
            logging.warning("Lane does not exist" + str(laneId))
            return

        if carId in self.cars:
            pass #unregister all cells related
        
    '''def drawRegisteredCells(self, painter, time):
        cells = self.cellReg.getAllCells(time)
        painter.setOpacity(0.3)
        for cell in cells:
            painter.fillRect(self.area.getCellRect(cell), Qt.blue)'''