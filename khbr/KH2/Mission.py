import os
from khbr._config import KH2_DIR

class Mission:
    def __init__(self, name, info):
        self.fn = self.get_fn(name)
        self.data = self.read_data()
        self.info = info

    def get_fn(self, name):
        return os.path.join(KH2_DIR, "KH2", "msn", "jp", name+".bar")

    def read_data(self):
        with open(self.fn, "rb") as f:
            return bytearray(f.read())

    def set_bonus_byte(self, value):
        self.set_list_byte(0x0D, value)

    def set_list_byte(self, offset, value):
        self.data[self.info.get("list_offset") + offset] = value
