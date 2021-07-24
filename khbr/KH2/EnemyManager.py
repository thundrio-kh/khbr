import json, os, yaml
from khbr._config import LIMITED_SIZE

class EnemyManager:
    def __init__(self, basepath):
        self.basepath = basepath
        with open(os.path.join(basepath, "full_enemy_records.json")) as f:
            self.enemy_records = json.load(f)
    def get_valid_enemies(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "enemy"]
    def get_valid_bosses(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "boss"]

    def get_enemies(self):
        enemies = self.get_valid_enemies()
        enabled_enemies = [self.enemy_records[e] for e in enemies if self.enemy_records[e]["enabled"]]
        return enabled_enemies

    def create_enemy_records(self, nightmare_mode=False, maxsize=LIMITED_SIZE, usefilters=["boss", "enabled", "nightmare"], getavail=True):
        defaults = {
            "replace_as": None,
            "source_replace_allowed": True,
            "model": None,
            "msn_replace_allowed": True,
            "tags": [],
            "category": None,
            "level": 0,
            "isnightmare": False,
            "parent": None,
            "variationof": None,
            "children": [],
            "hp": 100,
            "limiter": 1,
            "msn_required": False,
            "msn_source_as": None,
            "aimod": None,
            "can_be_enemy": False,
            "msn": None,
            "size": 0,
            "sizeTag": None, #sizeSmall sizeMedium sizeLarge 
            "room_size": 0,
            "roommaxsize": None,
            "enmp_index": None,
            "variations": [],
            "enabled": True,
            "blacklist_source": [],
            "blacklist_destination": [],
            "whitelist_source": [],
            "whitelist_destination": [],
            "adds": [],
            "subtracts": [],
            "msn_list": [],
            "program": None,
            "roomsizemultiplier": 1,
            "unchanged_file_size": False,
            "obj_edits": {}
        }
        with open(os.path.join(self.basepath, "enemies.yaml")) as f:
            bosses_f = yaml.load(f, Loader=yaml.FullLoader)
        bosses = {}
        kidlist = {}
        def _inheritConfig(parent, variation):
            for k in parent:
                if k == "variations":
                    if k not in variation:
                        variation[k] = list(parent[k].keys())
                    continue
                if k not in variation:
                    variation[k] = parent[k]
            for d in defaults:
                if d not in variation:
                    variation[d] = defaults[d]
                else:
                    if variation[d] == defaults[d] and d in parent:
                        if d not in ["children", "sizeTag"]:
                            variation[d] = parent[d]
        for name in bosses_f:
            main = bosses_f[name]
            for v in main["variations"]:
                variation = dict(main["variations"][v])
                variation["name"] = v
                _inheritConfig(main, variation)
                variation["category"] = '-'.join(sorted(variation["tags"]))
                if variation["sizeTag"]:
                    variation["category"] = "-".join([variation["category"], variation["sizeTag"]])

                if len(variation["category"]) > 0 and variation["category"][0] == "-":
                    variation["category"] = variation["category"][1:]
                if usefilters:
                    if "boss" in usefilters and variation["type"] != 'boss':
                        continue
                    if "enabled" in usefilters and not variation['enabled']:
                        continue
                    if "nightmare" in usefilters and nightmare_mode and not ("isnightmare" in variation and variation["isnightmare"]):
                        continue

                parent = variation["variationof"] or name
                assert parent != None
                if not variation["parent"]:
                    variation["parent"] = parent
                if parent not in kidlist:
                    kidlist[parent] = []
                kidlist[parent].append(name)
                
                bosses[v] = variation
        
        for parent in kidlist:
            bosses[parent]["children"] = sorted(list(set(kidlist[parent])))
            for child in bosses[parent]["children"]:
                _inheritConfig(bosses[parent], bosses[child])

        #
        if getavail:
            for source_name in bosses:
                source_boss = bosses[source_name]
                if not source_boss["type"] == "boss":
                    continue
                # Avail only needs to be filled in for the parent
                if not source_boss["parent"] == source_name:
                    continue
                avail = [] # These are bosses that are allowed to be here
                for dest_name in bosses:
                    dest_boss = bosses[dest_name]
                    if not dest_boss["type"] == "boss":
                        continue
                    if not dest_boss["parent"] == dest_name:
                        continue
                    if dest_boss["name"] == source_boss["name"]:
                        # Boss should always be allowed to be in it's own location
                        avail.append(dest_boss["name"])
                        continue
                    if not dest_boss["enabled"]:
                        continue
                    if source_boss["unchanged_file_size"] and (dest_boss["adds"] or dest_boss["subtracts"]):
                        continue
                    if not source_boss["source_replace_allowed"]:
                        continue
                    if dest_boss["blacklist_destination"]:
                        if source_name in dest_boss["blacklist_destination"]:
                            continue
                    if dest_boss["whitelist_destination"]:
                        if source_name not in dest_boss["whitelist_destination"]:
                            continue
                    if source_boss["blacklist_source"]:
                        if dest_name in source_boss["blacklist_source"]:
                            continue
                    if source_boss["whitelist_source"]:
                        if dest_name not in source_boss["whitelist_source"]:
                            continue
                    if not source_boss["msn_replace_allowed"]:
                        if dest_boss["msn_required"]:
                            continue
                    #print_debug("{} > {}: {} + {} >= {}".format(source_boss["name"], dest_boss["name"], source_boss["size"], dest_boss["room_size"], maxsize))
                    # THIS NEEDS TO CHANGE ONCE I CAN DO UNLIMITED STUFF
                    roommaxsize = source_boss["roommaxsize"] or maxsize
                    availablespace = (roommaxsize - source_boss["room_size"]) * source_boss["roomsizemultiplier"]
                    #print_debug("{} - {} ({}) >= 0".format(availablespace, source_boss["size"], availablespace - source_boss["size"]))
                    if availablespace - dest_boss["size"] < 0:
                        continue
                    avail.append(dest_boss["name"])
                source_boss["available"] = avail
        return bosses