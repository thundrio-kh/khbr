import os
from khbr._config import KH2_DIR

class Mission:
    def __init__(self, name, info):
        self.fn = self.get_fn(name)
        self.data = self.read_data()
        self.info = info
        self.modified = False

    def get_fn(self, name):
        return os.path.join(KH2_DIR, "KH2", "msn", "jp", name+".bar")

    def read_data(self):
        with open(self.fn, "rb") as f:
            return bytearray(f.read())

    def set_bonus_byte(self, value):
        self.set_list_byte(0x0D, value)

    def set_mickey_bit(self, boolean=False):
        self.set_flag_bit(10)

    def set_retry_bit(self, boolean=False):
        self.set_flag_bit(13)

    def set_xp_bit(self, boolean=False):
        self.set_flag_bit(11)

    def set_list_byte(self, offset, value):
        address = self.info.get("list_offset") + offset
        old_value = self.data[address]
        if old_value != value:
            self.modified = True
            self.data[address] = value

    def set_flag_bit(self, offset, boolean):
        flags = self.expand_flag_byte()
        flags[offset] = boolean
        new_byte = self.create_flag_byte()
        self.set_list_byte(0x04)