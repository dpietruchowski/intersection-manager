
class Manager:
    time_step = 3
    def __init__(self):
        self.cell_reg = CellRegistry()
        self.cars = {}

    def can_register(self, lane, begin_time, end_time):
        time_steps = range(end_time - begin_time)
        v = float(lane.length + lane.car_length) / (end_time - begin_time)
        distances = [v * time for time in time_steps]
        
        for time, distance in izip(time_steps, distances) :
            cells = lane.get_cells(distance)
            if not cells:
                logging.debug('There is no cells for distance %f' % distance)
                continue
            for cell in cells:
                if self.cell_reg.is_registered(time + begin_time, cell):
                    logging.debug('Cell is already registered %s' % str(cell))
                    return False

        return True

    def register(self, lane, carId, begin_time, end_time):
        start_time = ttt.time()
        if carId in self.cars:
            self.unregister(carId)

        if begin_time >= end_time:
            logging.debug('Begin time is greater than end time')
            return
        
        while not self.can_register(lane, begin_time, end_time):
            begin_time += self.time_step
            end_time += self.time_step

        time_steps = range(end_time - begin_time)
        v = float(lane.length + lane.car_length) / (end_time - begin_time)
        distances = [v * time for time in time_steps]
        for time, distance in izip(time_steps, distances):
            cells = lane.get_cells(distance)
            if not cells:
                logging.debug('There is no cells for distance %f' % distance)
                continue
            self.cars.setdefault(carId, []).append(time + begin_time)
            for cell in cells:
                self.cell_reg.register(time + begin_time, cell, carId)
        print("executrion time %f" % (ttt.time() - start_time))
        return (begin_time, end_time)
    
    def unregister(self, carId):
        if not carId in self.cars:
            return
        self.cell_reg.unregister_all(carId)
        del self.cars[carId]