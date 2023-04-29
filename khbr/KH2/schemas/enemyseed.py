from dataclasses import dataclass
from khbr.KH2.LocationManager import LocationManager
from khbr.randutils import create_new_entity
from khbr.KH2.schemas.random_config import RandomConfig

class EnemySeed:
    def __init__(self, config: RandomConfig, location_manager: LocationManager):
        self.spawns = {}
        self.subtract_map = {}
        self.spawn_limiters = {}
        self.msn_mapping = {}
        self.set_scaling = {}
        self.object_map = {}
        self.ai_mods = {}
        self.lua_mods = []
        self.utility_mods = {}
        self.cmd_mods = {}
        self.data_replacements = {}
        self.config = config
        self.location_manager = location_manager

        # Temporary option needed during generating wild enemies to track enemies already used per room
        self.wild_enemy_set = set()

    def toJson(self):
        return {
            "utility_mods": self.utility_mods,
            "spawns": self.spawns, 
            "msn_map": self.msn_mapping, 
            "ai_mods": self.ai_mods, 
            "lua_mods": list(set(self.lua_mods)),
            "cmd_mods": self.cmd_mods,
            "object_map": self.object_map, 
            "scale_map": self.set_scaling, 
            "limiter_map": self.spawn_limiters, 
            "subtract_map": self.subtract_map,
            "memory_expansion": self.config.memory_expansion
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
        if old_boss_object["name"] == new_boss_object["name"]:
            return # shouldn't do anything in this case, which is mostly only going to happen on selected enemy
        if new_boss_object["name"] == "Shadow Roxas":
            return # Nothing to do in this case
        self.update_extras(old_boss_object, new_boss_object, world, room, spawnpoint, spid)
        self.update_objentry(new_boss_object)
        self.update_aimod(old_boss_object, new_boss_object, worldnum=self.location_manager.get_world_num(room), roomnum=self.location_manager.get_room_num(room))
        self.update_luamod(new_boss_object)
        self.add_cmdmod(new_boss_object)
        if old_boss_object["type"] == "boss":
            self.update_msn_mapping(old_boss_object, new_boss_object)
            self.update_scaling(old_boss_object, new_boss_object)

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
            # TODO maybe this is the issue behind hades? It messes with mickey rule in some spotstoo
            if not old_boss_object["msn"]:
                if old_boss_object["msn_list"]:
                    return
            if not new_boss_object["msn"]:
                if new_boss_object["msn_list"]:
                    return
            msn_object = {"name": new_boss_object["msn"]}
        elif old_boss_object["msn_replace_allowed"] and not new_boss_object["msn_replace_allowed"]:
            msn_object = {"name": "WI03_MS104"}
        elif old_boss_object["msn_source_as"]:
            msn_object = {"name": old_boss_object["msn_source_as"]}
        else:
            # keeping old msn, but this picking the first item in the msn list might not work
            msn_object = {"name": self._get_msn_name(old_boss_object)}
        msn_object["setmickey"] = self._should_place_mickey(old_boss_object, new_boss_object)
        if old_boss_object["name"] == "Hades Cups":
            return # fixme MSN should not be replaced in this instance, also more thinking but maybe this should just be a condition on msn_replace_allowed
        if "roxas" in old_boss_object.get("tags") or "broken_mickey" in old_boss_object.get("tags"):
            msn_object["setmickey"] = False # Fights as roxas will tpose when summoning mickey
        if "disablecamera" in new_boss_object.get("tags"):
            msn_object["disablecamera"] = True
        if old_boss_object["final_fight"]:
            msn_object["setretry"] = True
        elif new_boss_object["final_fight"]:
            msn_object["setretry"] = False
        self.msn_mapping[self._get_msn_name(old_boss_object)] = msn_object

    @staticmethod
    def _get_msn_name(boss_object):
        if boss_object["msn"]:
            return boss_object["msn"]
        return boss_object["msn_list"][0]["msn"]

    def _should_place_mickey(self, old_boss_object, new_boss_object):
        mickey_rule = self.config.mickey_rule
        if mickey_rule == 'all':
            return True
        if mickey_rule == 'none':
            return False
        if mickey_rule == 'follow':
            return new_boss_object["mickey_source"]
        if mickey_rule == 'stay':
            return old_boss_object["mickey_source"]

    def update_scaling(self, old_boss_object, new_boss_object):
        if new_boss_object["name"] not in self.set_scaling:
            if "sourcemaxhp" in old_boss_object["tags"]:
                # We don't need this functionality anymore really
                # I think this will be fine because it's all in stt but could theoretically overload the max hp display which crashes with scan
                self.set_scaling[new_boss_object["name"]] = 5000 
        if self.config.scale_boss:
            if new_boss_object["name"] not in self.set_scaling:
                # In case of multiples of the same new boss, priotizes first boss
                self.set_scaling[new_boss_object["name"]] = old_boss_object["name"]

    def update_objentry(self, new_boss_object):
        if new_boss_object["obj_edits"]:
            self.object_map[new_boss_object["obj_id"]] = new_boss_object["obj_edits"]

    def add_ai(self, mod):
        modname = mod["name"]
        if not modname in self.ai_mods:
            self.ai_mods[modname] = [dict(mod)]
        else:
           
            for ex_mod in self.ai_mods[modname]:
                if ex_mod == mod:
                    return # Don't add the same mod, but if it's different, add it
            self.ai_mods[modname].append(dict(mod))

    def update_aimod(self, old_boss_object, new_boss_object, worldnum=0, roomnum=0):
        print("Updating:{}".format(self.ai_mods.get('B_CA000/b_ca.bdscript')))
        keys_to_check = {
            "old_boss": old_boss_object,
            "new_boss": new_boss_object
        }

        mods = [dict(mod) for mod in new_boss_object.get("aimods", []) if mod.get("source", "new") == "new"]
        mods += [dict(mod) for mod in old_boss_object.get("aimods", []) if mod.get("source", "new") == "old"]
        for add in new_boss_object["adds"]:
            mods += [dict(mod) for mod in add.get("aimods",[]) if mod.get("source", "new") == "new"]
            mods += [dict(mod) for mod in add.get("aimods",[]) if mod.get("source", "old") == "new"]

        for mod in mods:
            vars = mod.get("vars", {})
            for k,v in mod.get("replacements",{}).items():
                if v not in vars:
                    vars[v] = None # This should get filled in next
            for var in vars:
                for ktc in keys_to_check:
                    if var.startswith(ktc):
                        key = var.split(".")[1]
                        value = keys_to_check[ktc].get(key)
                        vars[var] = value

            vars["world"] = worldnum
            vars["room"] = roomnum

            mod["vars"] = vars

            self.add_ai(mod)

    def update_luamod(self, new_boss_object):
        if new_boss_object.get("luamod"):
            self.lua_mods.append(new_boss_object["luamod"])
            
    def add_cmdmod(self, new_boss_object):
        for cmd_mod in new_boss_object["cmdmods"]:
            if cmd_mod["value"] in self.cmd_mods:
                print("Warning: cmd mod {} getting overwritten by {}".format(cmd_mod["value"], new_boss_object["name"]))
            self.cmd_mods[cmd_mod["value"]] = cmd_mod["changes"]

    def set_data_final_xemnas_retry(self, shouldretry):
        msn_name = "EH20_MS113_RE"
        if msn_name in self.msn_mapping:
            self.msn_mapping[msn_name]["setretry"] = shouldretry
        elif shouldretry: # If not shouldretry, don't need to do anything
            self.msn_mapping[msn_name] = {"name": msn_name, "setretry": True}

    def set_dark_thorn_retry(self, shouldretry):
        msn_name = "BB05_MS104B"
        if msn_name in self.msn_mapping:
            self.msn_mapping[msn_name]["setretry"] = shouldretry
        elif shouldretry: # If not shouldretry, don't need to do anything
            self.msn_mapping[msn_name] = {"name": msn_name, "setretry": True}

    def add_xp_for_cups(self):
        cups_msns = [
            "HE_COL_1_8",
            "HE_COL_1_10",
            "HE_COL_2_10",
            "HE_COL_4_1",
            "HE_COL_4_2",
            "HE_COL_4_3",
            "HE_COL_4_4",
            "HE_COL_4_5",
            "HE_COL_4_6",
            "HE_COL_4_7",
            "HE_COL_4_8",
            "HE_COL_4_9",
            "HE_COL_4_10",
            "HE_COL_5",
            "HE_COL_5_8",
            "HE_COL_5_10",
            "HE_COL_6_10",
            "HE_COL_8_5",
            "HE_COL_8_6",
            "HE_COL_8_10",
            "HE_COL_8_25",
            "HE_COL_8_30",
            "HE_COL_8_31",
            "HE_COL_8_35",
            "HE_COL_8_40",
            "HE_COL_8_45",
            "HE_COL_8_49",
            "HE_COL_8_50",
            "HE_COL_8PP_BOSS",
            "HE_COL_8TI_BOSS",
            "HE_COLOSSEUM",
            "HE_COLOSSEUM_2_FOG",
            "HE_COLOSSEUM_3",
            "HE_COLOSSEUM_6",
            "HE_COLOSSEUM_6_FOG",
            "HE_COLOSSEUM_7",
            "HE_COLOSSEUM_8",
            "HE_COLOSSEUM_8_CEL",
            "HE_COLOSSEUM_8_ONLY",
            "HE_COLOSSEUM_8_PP",
            "HE_COLOSSEUM_8_TIT"
        ]
        for cup in cups_msns:
            if cup in self.msn_mapping:
                continue # Used by a boss so no xp anyway, ignore
            self.msn_mapping[cup] = {"name": cup, "setxp": True}