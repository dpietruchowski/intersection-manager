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
        if not self.find_cell(time, cell):
            item = Item()
            item.cell = cell
            item.id = id
            self.reg.setdefault(time, []).append(item)

    def unregister(self, time, id):
        items = self.reg[time]
        self.reg[time] = [item for item in items if item.id != id]

    def unregister_all(self, id):
        for time in self.reg.keys():
            self.unregister(time, id)
                 
    def get_id(self, time, cell):
        item = self.find_cell(time, cell)
        if item:
            return item.id
        return None

    def get_all_cells(self, time = None, id = None):
        cells = []
        if time in self.reg:
            for item in self.reg[time]:
                if id and item.id == id:
                    cells.append(item.cell)
                elif not id:
                    cells.append(item.cell)
        return cells

    def find_cell(self, time, cell):
        if time in self.reg:
            for item in self.reg[time]:
                if item.cell == cell:
                    return item
        return None

class Manager:
    def __init__(self):
        self.cell_reg = CellRegister()
        self.cars = {}

    def register(self, lane, carId, begin_time, end_time):
        if carId in self.cars:
            self.unregister(carId)

        if begin_time >= end_time:
            logging.warning('Begin time is greater than end time')
            return

        time_steps = range(end_time - begin_time)
        v = float(lane.length) / (end_time - begin_time)
        distances = [v * time for time in time_steps]
        
        for time, distance in izip(time_steps, distances) :
            cells = lane.get_cells(distance)
            if not cells:
                logging.warning('There is no cells for distance %f' % distance)
                continue
            for cell in cells:
                if not not self.cell_reg.find_cell(time + begin_time, cell):
                    logging.warning('Cell is already registered %s' % str(cell))
                    return

        for time, distance in izip(time_steps,distances):
            cells = lane.get_cells(distance)
            if not cells:
                print lane.length
                print time_steps
                print distances
                logging.warning('There is no cells for distance %f' % distance)
                continue
            self.cars.setdefault(carId, []).append(time + begin_time)
            for cell in cells:
                self.cell_reg.register(time + begin_time, cell, carId)
    
    def unregister(self, carId):
        if not carId in self.cars:
            return
        self.cell_reg.unregister_all(carId)
        del self.cars[carId]
