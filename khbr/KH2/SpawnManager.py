

import os

import yaml
from khbr.randutils import pick_boss_to_replace, pick_enemy_to_replace
from khbr._config import KH2_DIR
import random
class SpawnManager:
    def __init__(self):
        self.boss_enemies = [] # Gets filled as a cache
        self.spawns = None
        self.roommodedits = {
            "ax2_99": self.ax2_99,
            "ax2_40": self.ax2_40,
            "ax2_50": self.ax2_50,
            "stormrider_61": self.stormrider_61
        }

    # TODO 
    # I don't think this is needed
    # def set_spawns(self):
    #     if not self.spawns:
    #         self.spawns = self.get_locations()

    def modify_spawn(self, editname, spawnpoint):
        if editname not in self.roommodedits:
            print("Warning: could not find {} method for editing spawn, leaving unmodified".format(editname))
            return
        self.roommodedits(spawnpoint)

    def ax2_99(self, spawnpoint):
        # set the characters Y values and X values properly
        sora = spawnpoint[0]["Entities"][0]
        sora["PositionY"] = 14940
        # track for later
        bossz = float(sora["PositionZ"])
        sora["PositionZ"] = float(spawnpoint[0]["Entities"][2]["PositionZ"])

        riku = spawnpoint[0]["Entities"][1]
        riku["PositionY"] = 14940
        riku["PositionZ"] = float(spawnpoint[0]["Entities"][2]["PositionZ"])

        boss = spawnpoint[0]["Entities"][2]
        boss["PositionY"] = 14940
        boss["PositionZ"] = bossz

    def ax2_40(self, spawnpoint):
        # remove the buildings
        for spid in spawnpoint:
            spid["Entities"] = []

    def ax2_50(self, spawnpoint):
        # remove the dragon
        spawnpoint[0]["Entities"] = []

    def stormrider_61(self, spawnpoint):
        # move enemies height to the bottom
        sora = spawnpoint[0]["Entities"][0]
        sora["PositionY"] = 0

        donald = spawnpoint[0]["Entities"][1]
        donald["PositionY"] = 0

        goofy = spawnpoint[0]["Entities"][2]
        goofy["PositionY"] = 0

        boss = spawnpoint[0]["Entities"][3]
        boss["PositionY"] = 0

    def apply_room_mods(self, basespawns, ardname):
        roommods = {}
        if "roommodedits" in basespawns:
            for rm in basespawns["roommodedits"]:
                existing_rm = self.getSpawnpoint(ardname, rm)
                self.roommodedits[basespawns["roommodedits"][rm]](existing_rm)
                roommods[rm] = existing_rm
        return roommods

    @staticmethod
    def subtract_spawns(original_yaml, entities_to_remove):
        # TODO might need another pass
        if entities_to_remove:
            for sp_instance in original_yaml:
                toremove = []
                for e in range(len(sp_instance["Entities"])):
                    ent = sp_instance["Entities"][e]
                    for etr in entities_to_remove:
                        if ent["ObjectId"] == etr["ObjectId"]:
                            if "Argument1" in etr and etr["Argument1"] != ent["Argument1"]:
                                continue
                            if "Argument2" in etr and etr["Argument2"] != ent["Argument2"]:
                                continue
                            toremove.append(e)
                for e in sorted(list(set(toremove)))[::-1]:
                    sp_instance["Entities"].pop(e)

    @staticmethod
    def add_new_object(original_spawns, new_spawn_descriptor):
        # adding new entity to list, defaulting all values to the first entity in the list
        new_ent = dict(original_spawns["Entities"][0])
        # TODO Make a unique serial for the spawnpoint?? Maybe 6xx
        for attr in new_spawn_descriptor:
            if attr.startswith("mod"):
                baseattr = attr[3:]
                new_ent[baseattr] = new_ent[baseattr] + new_spawn_descriptor[attr]
            elif attr in new_ent:
                new_ent[attr] = new_spawn_descriptor[attr]

        # put the new entity in the existing sp_instance
        original_spawns["Entities"].append(new_ent)

        # set the ent index to the proper value
        new_spawn_descriptor["index"] = len(original_spawns["Entities"])-1

    @staticmethod
    def set_object_by_id(old_spawn, new_spawn_descriptor):
        for k in new_spawn_descriptor:
            if k == "name":
                old_spawn["ObjectId"] = new_spawn_descriptor[k]
            elif k == "index":
                pass
            else:
                old_spawn[k] = new_spawn_descriptor[k]

    @staticmethod
    def set_object_by_rec(old_spawn, obj):
        oid = obj["obj_id"]
        vrs = obj["vars"]

        old_spawn["ObjectId"] = oid
        old_spawn["Argument1"] = vrs[0]
        old_spawn["Argument2"] = vrs[1]

    @staticmethod
    def getSpawnpoint(ardname, spawnpoint, altspawns={}):
        if spawnpoint in altspawns.keys():
            return altspawns[spawnpoint]
        with open(os.path.join(KH2_DIR, "subfiles", "spawn", "ard", ardname, "{}.spawn".format(spawnpoint))) as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    @staticmethod
    def should_replace_enemy(old_enemy_object):
        if not old_enemy_object["source_replace_allowed"]:
            return False
        return True

    @staticmethod
    def should_replace_boss(old_boss, old_boss_parent, rand_seed):
        if old_boss["name"] in ["Final Xemnas (Clone)", "Final Xemnas (Clone) (Data)"]:
            return False # He gets removed later by subtracts, so don't replace
        if not old_boss["source_replace_allowed"] and old_boss["name"] != "Seifer (2)":
            return False
        if rand_seed.config.bossmode == "Wild" and "onetooneonly" in old_boss["tags"]:
            return False
        if rand_seed.bossmapping and old_boss_parent["name"] not in rand_seed.bossmapping:
            return False
        return True

    @staticmethod
    def get_new_boss(old_boss_object, old_boss_parent, config, rand_seed, enemy_records):
        # TODO SEIFER Can't be replaced here normally because it wants an enemy, so just put shadow roxas here
        if  old_boss_object["name"] == "Seifer (2)":
            return "Shadow Roxas"
        elif config.selected_boss:
            return  config.selected_boss
        else:
            new_boss_parent = None
            if rand_seed.bossmapping:
                new_boss_parent = rand_seed.bossmapping[old_boss_parent["name"]]

            if new_boss_parent:
                bosspicklist = [new_boss_parent]
            elif old_boss_parent["name"] in rand_seed.data_replacements:
                bosspicklist = [rand_seed.data_replacements[old_boss_parent["name"]]]
            else:
                bosspicklist = old_boss_parent["available"]
            new_boss = pick_boss_to_replace(enemy_records, bosspicklist)

            if "roxas" in old_boss_object["tags"]:
                if new_boss == "Axel (Data)":
                    # This fight is probably not very winnable as roxas, so force to normal axel II
                    return "Axel II"
            if "solo" in old_boss_object["tags"]:
                if new_boss == "Demyx (Data)":
                    return "Demyx" # Actual fix would be to just mod the ai to increase the time for destroying clones
            
            return new_boss
    
    @staticmethod
    def get_new_enemy(rand_seed, old_enemy_object):
        if rand_seed.config.selected_enemy:
            new_enemy = rand_seed.config.selected_enemy
        elif rand_seed.config.enemymode == "Wild":
            #TODO pretty sure this is broken, but also not safe to run in the game anyway
            new_enemy = pick_enemy_to_replace(old_enemy_object, rand_seed.config.enemies)
        elif rand_seed.enemymapping:
            if old_enemy_object["name"] not in rand_seed.enemymapping:
                return None # if it's not in mapping it's not enabled
            new_enemy = rand_seed.enemymapping[old_enemy_object["name"]]
        if rand_seed.config.bosses_replace_enemies and rand_seed.config.bosses:
            chance = 0.005
            if random.random() < chance:
                if not rand_seed.config.boss_enemies:
                    for boss_name in rand_seed.config.bosses:
                        boss = rand_seed.config.bosses[boss_name]
                        if boss["enabled"] and boss["can_be_enemy"]:
                            rand_seed.config.boss_enemies.append(boss_name)
                new_enemy = random.choice(rand_seed.config.boss_enemies)
        return new_enemy

    @staticmethod
    def getSpId(spawnpoint, idnum):
        for spid in spawnpoint:
            if spid["Id"] == idnum:
                return spid
        raise Exception("Spid not found!")