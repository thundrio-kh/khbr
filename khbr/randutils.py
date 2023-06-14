import random, struct

DEBUG_BOSS_LIST = None
#DEBUG_BOSS_LIST = {'Xemnas': 'Volcano Lord'}

def pickbossmapping(enemy_records, parent_bossdict):
    if DEBUG_BOSS_LIST:
        return DEBUG_BOSS_LIST
    while 1:
        bosslist = [b for b in parent_bossdict if parent_bossdict[b]["name"] == parent_bossdict[b]["parent"]]
        chosen = {}
        for k in sorted(bosslist, key=lambda k: len(parent_bossdict[k]["available"])):
            avail = [b for b in enemy_records[k]["available"] if not b in chosen.values()]
            if len(avail) == 0:
                break
            else:
                chosen_new_boss = random.choice(avail)
                chosen[k] = chosen_new_boss
        if len(bosslist) == len(chosen):
            return chosen

def pickenemymapping(enemy_records, categorized_enemies, spoilers=None, nightmare=None):
    # Create separate lists for each set of tags used by enemies
    # Every category needs some enemies, when nightmare is on this can sometimes fail during unit tests after changing categories
    mapping = {}
    for c in categorized_enemies:
        og = list(categorized_enemies[c].values()) # Remove duplicate parent entries
        new = list(og)
        if nightmare:
            new = [e for e in new if e["isnightmare"]]
        random.shuffle(new)
        for i in range(len(og)):
            old_parent = og[i]
            new_parent = new[i % len(new)]
            # So for each child of the new_parent, randomly pick a child of the old_parent
            # Then go through the variations of each, and add them to the mapping
            for old_child_name in old_parent["children"]:
                new_child_name = random.choice(new_parent["children"])
                new_child = enemy_records[new_child_name]
                old_child = enemy_records[old_child_name]
                for old_variation_name in old_child["variations"]:
                    new_variation_name = random.choice(list(new_child["variations"]))
                    mapping[old_variation_name] = new_variation_name
                    if spoilers is not None:
                        spoilers[old_variation_name] = new_variation_name

    return mapping
    #TODO unit test that len(enemylist) == len(list(mapping.keys()))
    
def pick_boss_to_replace(enemy_records, bossparentlist):
    enabled_parents = [b for b in bossparentlist if enemy_records[b]["enabled"]]
    if len(enabled_parents) == 0:
        raise Exception("No available parent bosses!")
    bossparent = enemy_records[random.choice(enabled_parents)]
    enabled_children = [b for b in bossparent["children"] if enemy_records[b]["enabled"]]
    if len(enabled_children) == 0:
        raise Exception("{} has no enabled children!".format(bossparent["name"]))
    bosschild = enemy_records[random.choice(enabled_children)]
    enabled_variations = [b for b in bosschild["variations"] if enemy_records[b]["enabled"]]
    if len(enabled_variations) == 0:
        raise Exception("{} has no enabled variations!".format(bosschild["name"]))
    chosen_boss = random.choice(enabled_variations)
    return chosen_boss

def pick_enemy_to_replace(old_enemy, enabled_enemies, enemy_set={}, max_enemies=0):
    new_options = [e["name"] for e in enabled_enemies if e["category"] == old_enemy["category"]]
    pick = random.choice(new_options)
    if max_enemies > 0:
        if len(enemy_set) < max_enemies:
            enemy_set.add(pick)
        else:
            max_options = list(enemy_set.intersection(set(new_options)))
            if len(max_options) == 0:
                pick = old_enemy["name"] # fallback hopefully doesn't happen too often
            else:
                pick = random.choice(list(max_options))
    return pick

def create_new_entity(old_entity, new_object):
    if old_entity == "new":
        entity = dict(new_object)
        entity["index"] = "new"
        return entity
    entity = dict(old_entity)
    entity["name"] = new_object["name"]
    return entity

class BinaryReader:
    def __init__(self, fn=None, data=None):
        if data:
            self.data = data
        else:
            self.data = bytearray(open(fn, "rb").read())
        self.pos = 0
    def readType(self, tpe, unpack=False):
        result = {
            "float32": self.readFloat32,
            "int32": self.readInt32,
            "int16": self.readInt16,
            "byte": self.readByte
        }[tpe]()
        if unpack and tpe == "float32":
            return self.unpackFloat32(result)
        return result
    def readByte(self):
        b = self.data[self.pos]
        self.pos += 1
        return b
    def readRest(self):
        arr = bytearray()
        for _ in range(len(self.data)-self.pos):
            arr.append(self.readByte())
        return arr
    def readFloat32(self):
        import struct
        bts = bytearray([self.readByte() for _ in range(4)])
        return bts
    def unpackFloat32(self, bts):
        return struct.unpack('<f', bts)[0]
    def readInt32(self):
        bts = self.data[self.pos:self.pos+4]
        self.pos += 4
        return int.from_bytes(bts, byteorder="little")
    def readInt16(self):
        bts = self.data[self.pos:self.pos+2]
        self.pos += 2
        return int.from_bytes(bts, byteorder="little")


class BinaryWriter:
    def __init__(self, fn=None):
        self.bytes = bytearray()
        self.fp = open(fn, "wb") if fn else None
        self.nwrites = 0
    def writeType(self, tpe, data):
        return {
            "float32": self.writeFloat32,
            "int32": self.writeInt32,
            "int16": self.writeInt16,
            "byte": self.writeByte
        }[tpe](data)
    def writeBytes(self, b):
        if self.fp:
            self.fp.write(b)
        self.bytes += b
        self.nwrites += len(b)
        #print([hex(bt) for bt in b])
    def writeArray(self, arr):
        for b in arr:
            self.writeBytes(bytes(b))
    def writeFloat32(self, value):
        packed_value = struct.pack('<f',value)
        self.writeBytes(packed_value)
    def writeInt32(self, value):
        self.writeBytes(int.to_bytes(value, length=4, byteorder="little"))
    def writeInt16(self, value):
        self.writeBytes(int.to_bytes(value, length=2, byteorder="little"))
    def writeByte(self, value):
        self.writeBytes(int.to_bytes(value, length=1, byteorder="little"))
    def close(self):
        if self.fp:
            self.fp.close()
    def getBytes(self):
        return self.bytes