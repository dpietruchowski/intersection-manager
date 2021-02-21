

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
        
    def is_registered(self, time, cell):
        return not not self.find_cell(time, cell)

    def find_cell(self, time, cell):
        if time in self.reg:
            for item in self.reg[time]:
                if item.cell == cell:
                    return item
        return None



#####################################



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