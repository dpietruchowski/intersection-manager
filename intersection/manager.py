from junction import Cell, Lane

import ctypes
import time as ttt
import logging
import os
from itertools import izip

lib = ctypes.cdll.LoadLibrary('./intersection/cpp/libregister.so')
lib.Reg_new.restype = ctypes.c_void_p
lib.Reg_delete.argtypes = [ctypes.c_void_p]
lib.Reg_set_time.argtypes = [ctypes.c_void_p]
lib.Reg_register.argtypes = [ctypes.c_void_p]
lib.Reg_unregister_all.argtypes = [ctypes.c_void_p]
lib.Reg_get_registered_id.restype = ctypes.c_void_p
lib.Reg_get_registered_id.argtypes = [ctypes.c_void_p]
lib.Reg_free.argtypes = [ctypes.c_void_p]

class CellRegistry:
    def __init__(self):
        self.obj = lib.Reg_new()

    def __del__(self):
        lib.Reg_delete(self.obj)

    def set_time(self, time):
        lib.Reg_set_time(self.obj, time)

    def register(self, time, cell, id):
        lib.Reg_register(self.obj, time, str(id), cell.row, cell.col)

    def unregister_all(self, id):
        lib.Reg_unregister_all(self.obj, str(id))

    def get_registered_id(self, time, cell):
        ptr = lib.Reg_get_registered_id(self.obj, int(time), int(cell.row), int(cell.col))
        if not ptr:
            return None
        strid = ctypes.cast(ptr, ctypes.c_char_p).value
        lib.Reg_free(ptr)
        return strid

    def is_registered(self, time, cell):
        return not not self.get_registered_id(time, cell)


lib.Man_new.restype = ctypes.c_void_p
lib.Man_delete.argtypes = [ctypes.c_void_p]
lib.Man_can_register.argtypes = [ctypes.c_void_p, ctypes.py_object, ctypes.c_float, ctypes.c_float, ctypes.c_float]
lib.Man_register.argtypes = [ctypes.c_void_p, ctypes.py_object, ctypes.c_float, ctypes.c_float, ctypes.c_float]
lib.Man_unregister.argtypes = [ctypes.c_void_p]
lib.Man_is_cell_registered.argtypes = [ctypes.c_void_p]
lib.Man_set_time.argtypes = [ctypes.c_void_p]

class Manager:
    time_step = 3
    def __init__(self):
        self.obj = lib.Man_new()
        self.cars = {}

    def __del__(self):
        lib.Man_delete(self.obj)

    def can_register(self, lane, begin_time, end_time):
        return lib.Man_can_register(self.obj, lane, lane.length, lane.car_length, lane.car_width, begin_time, end_time)

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

        lib.Man_register(self.obj, lane, float(lane.length), lane.car_length, lane.car_width, str(carId), begin_time, end_time)
        print("Registration execution time %f" % (ttt.time() - start_time))
        return (begin_time, end_time)

    def unregister(self, carId):
        if not carId in self.cars:
            return
        return lib.unregister(self.obj, str(carId))

    def is_cell_registered(self, time, cell):
        return lib.Man_is_cell_registered(self.obj, time, cell.row, cell.col)

    def set_time(self, time):
        lib.Man_set_time(self.obj, time)

    