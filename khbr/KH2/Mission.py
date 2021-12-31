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
        self.set_flag_bit(14, boolean)

    def set_retry_bit(self, boolean=False):
        self.set_flag_bit(11, boolean)

    def set_noxp_bit(self, boolean=False):
        self.set_flag_bit(13, boolean)

    def get_list_byte(self, offset):
        address = self.info.get("list_offset") + offset
        old_value = self.data[address]
        return old_value

    def set_list_byte(self, offset, value):
        address = self.info.get("list_offset") + offset
        old_value = self.data[address]
        if old_value != value:
            self.modified = True
            self.data[address] = value

    def set_flag_bit(self, offset, boolean):
        old_byte_1 = self.get_list_byte(0x04)
        old_byte_2 = self.get_list_byte(0x05)
        flags = self.expand_flag_bytes(old_byte_1, old_byte_2)
        flags[offset] = '1' if boolean else '0'
        new_byte_1, new_byte_2 = self.create_flag_byte(flags)
        self.set_list_byte(0x04, int(new_byte_1, 16))
        self.set_list_byte(0x05, int(new_byte_2, 16))

    def expand_flag_bytes(self, byte_1, byte_2):
        return self.expand_flag_byte(byte_1)+self.expand_flag_byte(byte_2)

    @staticmethod
    def expand_flag_byte(byte):
        if type(byte) == str:
            byte = int(byte, 16)
        return list(bin(byte)[2:].zfill(8))

    @staticmethod
    def create_flag_byte(flags):
        byte_1 = hex(int(''.join(flags[:8]), 2))[2:]
        byte_2 = hex(int(''.join(flags[8:]), 2))[2:]
        return byte_1, byte_2