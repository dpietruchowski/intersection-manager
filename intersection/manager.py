from junction import Cell, Lane

import logging
from itertools import izip

class Item:
    def __repr__(self):
        return repr('Item|' + str(self.cell) +', ' + str(self.id) + '|')

class CellRegister:
    def __init__(self):
        self.reg = {}

    def register(self, time, cell, id):
        if not self.findCell(time, cell):
            item = Item()
            item.cell = cell
            item.id = id
            self.reg.setdefault(time, []).append(item)

    def unregister(self, time, id):
        items = self.reg[time]
        self.reg[time] = [item for item in items if item.id != id]

    def unregisterAll(self, id):
        for time in self.reg.keys():
            self.unregister(time, id)
                 
    def getId(self, time, cell):
        item = self.findCell(time, cell)
        if item:
            return item.id
        return None

    def getAllCells(self, time = None, id = None):
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

    def register(self, lane, carId, beginTime, endTime):
        if carId in self.cars:
            self.unregister(carId)

        if beginTime >= endTime:
            logging.warning('Begin time is greater than end time')
            return

        timeSteps = range(endTime - beginTime)
        v = float(lane.length) / (endTime - beginTime)
        distances = [v * time for time in timeSteps]
        
        for time, distance in izip(timeSteps,distances) :
            cells = lane.getCells(distance)
            if not cells:
                logging.warning('There is no cells for distance %f' % distance)
                continue
            for cell in cells:
                if not not self.cellReg.findCell(time + beginTime, cell):
                    logging.warning('Cell is already registered %s' % str(cell))
                    return

        for time, distance in izip(timeSteps,distances):
            cells = lane.getCells(distance)
            if not cells:
                print lane.length
                print timeSteps
                print distances
                logging.warning('There is no cells for distance %f' % distance)
                continue
            self.cars.setdefault(carId, []).append(time + beginTime)
            for cell in cells:
                self.cellReg.register(time + beginTime, cell, carId)
    
    def unregister(self, carId):
        if not carId in self.cars:
            return
        self.cellReg.unregisterAll(carId)
        del self.cars[carId]
