# Really at the same time you make party member rando you should make costume rando, it's just as easy
import random
from khbr.randutils import BinaryReader, BinaryWriter
import os

class MemtManager:
    def __init__(self, binfn):
        self.schema = [
            ("World ID", "int16"),
            ("World Story Flag/ID", "int16"),
            ("World Story Flag/ID Negation", "int16"),
            ("Unknown1", "int16"),
            ("Unknown2", "int16"),
            ("Unknown3", "int16"),
            ("Unknown4", "int16"),
            ("Unknown5", "int16"),
            ("Player (Sora)", "int16"),
            ("Friend 1 (Donald)", "int16"),
            ("Friend 2 (Goofy)", "int16"),
            ("World Character", "int16"),
            ("Player (Valor)", "int16"),
            ("Player (Wisdom)", "int16"),
            ("Player (Limit)", "int16"),
            ("Player (Master)", "int16"),
            ("Player (Final)", "int16"),
            ("Player (Anti)", "int16"),
            ("Player (Mickey)", "int16"),
            ("Player (Sora High Poly)", "int16"),
            ("Player (Valor High Poly)", "int16"),
            ("Player (Wisdom High Poly)", "int16"),
            ("Player (Limit High Poly)", "int16"),
            ("Player (Master High Poly)", "int16"),
            ("Player (Final High Poly)", "int16"),
            ("Player (Sora High Poly)", "int16"),
        ]
        self.read_bin(binfn)

        self.sora_keys = [
            "Player (Sora)",
            "Player (Valor)",
            "Player (Wisdom)",
            "Player (Limit)",
            "Player (Master)",
            "Player (Final)",
            "Player (Anti)",
            "Player (Sora High Poly)",
            "Player (Valor High Poly)",
            "Player (Wisdom High Poly)",
            "Player (Limit High Poly)",
            "Player (Master High Poly)",
            "Player (Final High Poly)"
        ]

        self.costumes = {
            "sora": {
                "Player (Sora)": {
                    "v": 84,
                    "wi": 1623,
                    "nm": 693,
                    "xm": 2389,
                    "tr": 1622
                },
                "Player (Valor)": {
                    "v": 85,
                    "wi": 1642,
                    "nm": 998,
                    "xm": 2390,
                    "tr": 1641
                },
                "Player (Wisdom)": {
                    "v": 86,
                    "wi": 1644,
                    "nm": 999,
                    "xm": 2391,
                    "tr": 1643
                },
                "Player (Limit)": {
                    "v": 2397,
                    "wi": 2401,
                    "nm": 2398,
                    "xm": 2399,
                    "tr": 2400
                },
                "Player (Master)": {
                    "v": 87,
                    "wi": 1646,
                    "nm": 1000,
                    "xm": 2392,
                    "tr": 1645
                },
                "Player (Final)": {
                    "v": 88,
                    "wi": 1648,
                    "nm": 1001,
                    "xm": 2393,
                    "tr": 1647
                },
                "Player (Anti)": {
                    "v": 89,
                    "wi": 1650,
                    "nm": 1002,
                    "xm": 2394,
                    "tr": 1649
                },
                "Player (Sora High Poly)": {
                    "v": 264,
                    "wi": 1623, # Technically no high poly for wi I think it will work out fine
                    "nm": 1813,
                    "xm": 2433,
                    "tr": 1685,
                },
                "Player (Valor High Poly)": {
                    "v": 200,
                    "wi": 1642, # Technically no high poly for wi I think it will work out fine
                    "nm": 1814,
                    "xm": 2434,
                    "tr": 1686,
                },
                "Player (Wisdom High Poly)": {
                    "v": 1529,
                    "wi": 1644, # Technically no high poly for wi I think it will work out fine
                    "nm": 1815,
                    "xm": 2435,
                    "tr": 1687,
                },
                "Player (Limit High Poly)": {
                    "v": 2431,
                    "wi": 2401, # Technically no high poly for wi I think it will work out fine
                    "nm": 2432,
                    "xm": 2438,
                    "tr": 2439,
                },
                "Player (Master High Poly)": {
                    "v": 1530,
                    "wi": 1646, # Technically no high poly for wi I think it will work out fine
                    "nm": 1816,
                    "xm": 2436,
                    "tr": 1688,
                },
                "Player (Final High Poly)": {
                    "v": 1531,
                    "wi": 1648, # Technically no high poly for wi I think it will work out fine
                    "nm": 1817,
                    "xm": 2437,
                    "tr": 1690,
                }
            },
            "Friend 1 (Donald)": {
                "v": 92,
                "wi": 1487,
                "nm": 670,
                "xm": 2395,
                "tr": 1370
            },
            "Friend 2 (Goofy)": {
                "v": 93,
                "wi": 1269,
                "nm": 669,
                "xm": 2396,
                "tr": 1364
            }
        }
        self.costume_map = {}
        for k,v in self.costumes.items():
            if k == "sora":
                for k2,v2 in v.items():
                    for k3, v3 in v2.items():
                        self.costume_map[v3] = k3
            else:
                for k,v in v.items():
                    self.costume_map[v] = k

        # have to fix simba limit...

        self.party_members = {
            # Can't randomize donald and goofy party members... the game gets pretty unstable with two world characters out at once unfortunately
            # "donald": [92, 1487, 670, 2395, 1370, 1519], #1519 is lk
            # "goofy": [93, 1269, 669, 2396, 1364, 1563], # 1563 is lk
            "jack_skellington": [95, 96],
            "aladdin": [98],
            "mulan": [99, 100],
            "auron": [101],
            "simba": [97], # Test because limit with human sora might break
            "riku": [2073, 2257],
            "tron": [724],
            "beast": [94],
            "jack_sparrow": [2077, 2078]
        }
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
    memt = MemtManager(os.path.join(os.path.dirname(__file__), "data", "bin", "memt.bin"))

    # Costume rando
    wtypes = ["v", "wi", "nm", "xm", "tr"]
    replacements = {}
    sora_shuffled = list(wtypes)
    random.shuffle(sora_shuffled)
    sora_replacements = {wtypes[i]:sora_shuffled[i] for i in range(len(wtypes))}
    donald_shuffled = list(wtypes)
    random.shuffle(donald_shuffled)
    donald_replacements = {wtypes[i]:donald_shuffled[i] for i in range(len(wtypes))}
    goofy_shuffled = list(wtypes)
    random.shuffle(goofy_shuffled)
    goofy_replacements = {wtypes[i]:goofy_shuffled[i] for i in range(len(wtypes))}

    for entry in memt.entries:
        for k in sora_keys:
            old_value = entry[k]
            if old_value in costume_map:
                category = costume_map[old_value]
                new_category = sora_replacements[category]
                new_value = costumes["sora"][k][new_category]
                entry[k] = new_value
        old_value = entry["Friend 1 (Donald)"]
        if old_value in costume_map:
            category = costume_map[old_value]
            new_category = donald_replacements[category]
            new_value = costumes["Friend 1 (Donald)"][new_category]
            entry["Friend 1 (Donald)"] = new_value
        old_value = entry["Friend 2 (Goofy)"]
        if old_value in costume_map:
            category = costume_map[old_value]
            new_category = goofy_replacements[category]
            new_value = costumes["Friend 2 (Goofy)"][new_category]
            entry["Friend 2 (Goofy)"] = new_value

    # Party member rando

    party_member_map = {}
    for k,v in party_members.items():
        for obj_id in v:
            party_member_map[obj_id] = k
    original = list(party_members.keys())
    shuffled = list(party_members.keys())
    random.shuffle(shuffled)
    replacements = {}
    for i in range(len(original)):
        replacements[original[i]] = shuffled[i]
    for entry in memt.entries:
        # donald_value = entry["Friend 1 (Donald)"]
        # if donald_value in party_members["donald"]: # that means we are allowed to change the value
        #     entry["Friend 1 (Donald)"] = random.choice(party_members[replacements["donald"]])
        # goofy_value = entry["Friend 2 (Goofy)"]
        # if goofy_value in party_members["goofy"]: # that means we are allowed to change the value
        #     entry["Friend 1 (Goofy)"] = random.choice(party_members[replacements["goofy"]])
        worldvalue = entry["World Character"]
        if worldvalue:
            worldfriend = party_member_map[worldvalue]
        entry["World Character"] = random.choice(party_members[replacements[worldfriend]])
    print(replacements)

    memt.write_bin("C:\\Users\\12sam\\Desktop\\openkh\\mods\\kh2\\thundrio-kh\\devmod\\files\\root\\memt.list")
