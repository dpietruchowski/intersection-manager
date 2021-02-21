import ctypes
import pdb

lib = ctypes.cdll.LoadLibrary('./libregister.so')
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

    def register(self, time, row, col, id):
        lib.Reg_register(self.obj, time, str(id), row, col)

    def unregister_all(self, id):
        lib.Reg_unregister_all(self.obj, str(id))

    def get_registered_id(self, time, row, col):
        ptr = lib.Reg_get_registered_id(self.obj, time, row, col)
        if not ptr:
            return None
        strid = ctypes.cast(ptr, ctypes.c_char_p).value
        lib.Reg_free(ptr)
        return strid

    def is_registered(self, time, row, col):
        return not not self.get_registered_id(time, row, col)

if __name__ == "__main__":
    reg = CellRegistry()
    #pdb.set_trace()
    reg.register(9, 0, 0, "vehicle_0")
    reg.register(9, 1, 2, "vehicle_3")
    reg.register(4, 1, 1, "vehicle_1")
    reg.register(2, 0, 0, "vehicle_2")
    reg.set_time(5)
    print reg.get_registered_id(9, 0, 0)
    print reg.get_registered_id(9, 1, 2)
    print reg.get_registered_id(9, 2, 2)
    print reg.get_registered_id(4, 1, 1)
    print reg.get_registered_id(2, 0, 0)
    print reg.is_registered(9, 2, 2)
    print reg.is_registered(4, 1, 1)
    print reg.is_registered(2, 0, 0)