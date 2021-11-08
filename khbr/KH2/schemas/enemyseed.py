from dataclasses import dataclass
from khbr.randutils import create_new_entity
from khbr.KH2.schemas.random_config import RandomConfig

class EnemySeed:
    def __init__(self, config: RandomConfig):
        self.spawns = {}
        self.subtract_map = {}
        self.spawn_limiters = {}
        self.msn_mapping = {}
        self.set_scaling = {}
        self.object_map = {}
        self.ai_mods = {}
        self.utility_mods = {}
        self.data_replacements = {}
        self.config = config
            
    def toJson(self):
        return {
            "utility_mods": self.utility_mods,
            "spawns": self.spawns, 
            "msn_map": self.msn_mapping, 
            "ai_mods": list(set(self.ai_mods)), 
            "object_map": self.object_map, 
            "scale_map": self.set_scaling, 
            "limiter_map": self.spawn_limiters, 
            "subtract_map": self.subtract_map
            }

    def add_spawn(self, world, room, spawnpoint, spid, entity, new_boss_object):
        #'m pretty sure this is wrong because of update_extras
        new_entity = create_new_entity(entity, new_boss_object)
        if world not in self.spawns:
            self.spawns[world] = {}
        if room not in self.spawns[world]:
            self.spawns[world][room] = {"spawnpoints": {}}
        if spawnpoint not in self.spawns[world][room]["spawnpoints"]:
            self.spawns[world][room]["spawnpoints"][spawnpoint] = {"sp_ids": {}}
        if spid not in self.spawns[world][room]["spawnpoints"][spawnpoint]["sp_ids"]:
            self.spawns[world][room]["spawnpoints"][spawnpoint]["sp_ids"][spid] = []
        self.spawns[world][room]["spawnpoints"][spawnpoint]["sp_ids"][spid].append(new_entity)
        return

    def add_to_subtract_map(self, world, room, spawnpoint, objectid):
        if world not in self.subtract_map:
            self.subtract_map[world] = {}
        if room not in self.subtract_map[world]:
            self.subtract_map[world][room] = {"spawnpoints": {}}
        if spawnpoint not in self.subtract_map[world][room]["spawnpoints"]:
            self.subtract_map[world][room]["spawnpoints"][spawnpoint] = []
        self.subtract_map[world][room]["spawnpoints"][spawnpoint].append(objectid)

    def update_seed(self, old_boss_object, new_boss_object, world, room, spawnpoint, spid):
        if new_boss_object["name"] == "Shadow Roxas":
            return # Nothing to do in this case
        self.update_extras(old_boss_object, new_boss_object, world, room, spawnpoint, spid)
        self.update_msn_mapping(old_boss_object, new_boss_object)
        self.update_scaling(old_boss_object, new_boss_object)
        self.update_objentry(new_boss_object)
        self.update_aimod(old_boss_object, new_boss_object)

    def update_extras(self, old_boss_object, new_boss_object, world, room, spawnpoint, spid):
        # self, world, room, spawnpoint, spid, entity, new_boss_object
        # uggg my head hurts
        for obj in new_boss_object["adds"]:
            self.add_spawn(world, room, spawnpoint, spid, "new", obj)
        for obj in old_boss_object["subtracts"]+old_boss_object["adds"]:
            if "dontSub" in obj and obj["dontSub"]:
                continue
            self.add_to_subtract_map(world, room, spawnpoint, obj)

    def update_msn_mapping(self, old_boss_object, new_boss_object):
        if old_boss_object["msn_replace_allowed"] and new_boss_object["msn_replace_allowed"]:
            # This is fine because the only bosses with msn_list don't need the msn to be swapped
            if not old_boss_object["msn"]:
                if old_boss_object["msn_list"]:
                    return
            if not new_boss_object["msn"]:
                if new_boss_object["msn_list"]:
                    return
            self.msn_mapping[old_boss_object["msn"]] = new_boss_object["msn"]
        elif old_boss_object["msn_source_as"]:
            self.msn_mapping[old_boss_object["msn"]] = old_boss_object["msn_source_as"]

    def update_scaling(self, old_boss_object, new_boss_object):
        if new_boss_object["name"] not in self.set_scaling:
            if "sourcemaxhp" in old_boss_object["tags"]:
                # I think this will be fine because it's all in stt but could theoretically overload the max hp display which crashes with scan
                self.set_scaling[new_boss_object["name"]] = 5000 
        if self.config.scale_boss:
            if new_boss_object["name"] not in self.set_scaling:
                # In case of multiples of the same new boss, priotizes first boss
                self.set_scaling[new_boss_object["name"]] = old_boss_object["name"]

    def update_objentry(self, new_boss_object):
        if new_boss_object["obj_edits"]:
            self.object_map[new_boss_object["obj_id"]] = new_boss_object["obj_edits"]

    def update_aimod(self, old_boss_object, new_boss_object):
        if "aimod" in new_boss_object and new_boss_object["aimod"]:
            self.ai_mods[new_boss_object["name"]] = old_boss_object["name"]