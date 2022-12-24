import random
from khbr.randutils import BinaryReader, BinaryWriter
import os

class CommandManager:
    def __init__(self, binfn):
        self.schema = [
            ("Id", "int16"),
            ("Execute", "int16"),
            ("Argument", "int16"),
            ("Submenu", "byte"),
            ("Icon", "byte"),
            ("Text", "int32"),
            ("Flags", "int32"), # These are bitflags
            ("Range", "float32"),
            ("Dir", "float32"),
            ("Dir Range", "float32"),
            ("Mp/Drive Cost", "byte"),
            ("Camera", "byte"),
            ("Priority", "byte"),
            ("Receiver", "byte"),
            ("Time", "int16"),
            ("Require", "int16"),
            ("Mark", "byte"),
            ("Action", "byte"),
            ("Reaction Count", "int16"),
            ("Dist Range", "int16"),
            ("Score", "int16"),
            ("Disable Form", "int16"),
            ("Group", "byte"),
            ("Reserve", "byte")
        ]
        self.read_bin(binfn)
    def read_bin(self, fn):
        memt = BinaryReader(fn)
        self.file_version = memt.readInt32()
        self.num_entries = memt.readInt32()

        self.entries = []
        for _ in range(self.num_entries):
            ent = {}
            for ofs in self.schema:
                ent[ofs[0]] = memt.readType(ofs[1], unpack=True)
            self.entries.append(ent)
        # We don't care to edit the table at the end of the memt file, so just call it a generic "footer"
        self.footer = memt.readRest()
        if len(self.entries) != self.num_entries:
            raise Exception("Error, memt specified {} entries but only found {}".format(self.num_entries, len(self.entries)))
    def write_entries(self, bw):
        bw.writeInt32(self.file_version)
        bw.writeInt32(len(self.entries))
        for ent in self.entries:
            for ofs in self.schema:
                bw.writeType(tpe=ofs[1], data=ent[ofs[0]])
        bw.writeBytes(self.footer)
    def write_bin(self, outfn):
        new = BinaryWriter(outfn)
        self.write_entries(new)
        new.close()
    def dump_bin(self):
        new = BinaryWriter()
        self.write_entries(new)
        return new.getBytes()
    def get_unique_values(self, att):
        return {e[att] for e in self.entries}
    def update_entry(self, entry_index, changes):
        for k,v in changes.items():
            self.entries[entry_index][k] = v

if __name__ == "__main__":
    cmd = CommandManager(os.path.join(os.path.dirname(__file__), "data", "bin", "cmd.bin"))

    cmd.entries[604]["Flags"] = 4294967295
    
    cmd.write_bin("C:\\Users\\12sam\\Desktop\\openkh\\mods\\kh2\\thundrio-kh\\devmod\\files\\root\\cmd.list")
    #cmd.write_bin("C:\\Users\\12sam\\Desktop\\openkh\\mods\\kh2\\bossrush\\files\\root\\cmd.list")