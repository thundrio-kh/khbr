

import os

import yaml
from khbr.randutils import pick_boss_to_replace, pick_enemy_to_replace, log_output
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
            "stormrider_61": self.stormrider_61,
            "groundshaker": self.groundshaker,
            "shadow_stalker": self.shadow_stalker,
            "ax1_40": self.ax1_40,
            "jafar_60": self.jafar_60
        }


    # TODO 
    # I don't think this is needed
    # def set_spawns(self):
    #     if not self.spawns:
    #         self.spawns = self.get_locations()

    def modify_spawn(self, editname, spawnpoint):
        if editname not in self.roommodedits:
            log_output("Warning: could not find {} method for editing spawn, leaving unmodified".format(editname), log_level=0)
            return
        self.roommodedits(spawnpoint)

    def groundshaker(self, spawnpoint):
        groundshaker = spawnpoint[0]["Entities"][3]
        # Position groundshaker entity right in front of sora and at proper ground height
        groundshaker["PositionZ"] = 4330
        groundshaker["PositionY"] = -384

        for boss_add in spawnpoint[0]["Entities"][4:]:
            boss_add["PositionY"] = groundshaker["PositionY"]
            boss_add["PositionZ"] = groundshaker["PositionZ"]

    def ax1_40(self, spawnpoint):
        sora = spawnpoint[0]["Entities"][0]
        sora["PositionZ"] = -770

        friend1 = spawnpoint[0]["Entities"][1]
        friend1["PositionZ"] = -800

        friend2 = spawnpoint[0]["Entities"][2]
        friend2["PositionZ"] = -800

        # Lots of adds possible here, so find the boss
        for ent in spawnpoint[0]["Entities"]:
            if ent["PositionZ"] == 650:
                ent["PositionZ"] = -150
                ent["PositionY"] =-50

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

        for boss_add in spawnpoint[0]["Entities"][3:]:
            boss_add["PositionY"] = boss["PositionY"]
            boss_add["PositionZ"] = boss["PositionZ"]

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

    def shadow_stalker(self, spawnpoint):
        # move enemies height to the bottom
        sora = spawnpoint[0]["Entities"][0]

        boss = spawnpoint[0]["Entities"][3]
        boss["PositionY"] = sora["PositionY"]

    def jafar_60(self, spawnpoint):
        # move enemies height to the sora
        sora = spawnpoint[0]["Entities"][0]

        boss = spawnpoint[0]["Entities"][2]
        boss["PositionY"] = -22300 - 30 # start 30 above ground to handle things like marluxia
        sora["PositionY"] = -22300 - 30

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
    def add_new_object(original_spawns, new_spawn_descriptor, default_object=None):
        if new_spawn_descriptor["ObjectId"] == -1:
            return # -1 means was an object for making a custom unit, but shouldn't be added as an entity
        # TOTEST might need to pass in the default_object with coordinates but maybe not. test in Past Pete fight
        if not default_object:
            default_object = {
                "ObjectId": 0,
                "PositionX": 0,
                "PositionY": 0,
                "PositionZ": 0,
                "RotationX": 0,
                "RotationY": 0,
                "RotationZ": 0,
                "SpawnType": 0,
                "SpawnArgument": 0,
                "Serial": 0,
                "Argument1": 0,
                "Argument2": 0,
                "ReactionCommand": 0,
                "SpawnDelay": 0,
                "Command": 0,
                "SpawnRange": 0,
                "Level": 0,
                "Medal": 0
            }
        # adding new entity to list, defaulting all values to the first entity in the list
        new_ent = dict(original_spawns["Entities"][0])  if len(original_spawns["Entities"]) else dict(default_object)
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
        if rand_seed.config.bossmode == "One to One" and rand_seed.bossmapping and old_boss_parent["name"] not in rand_seed.bossmapping:
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
            if old_boss_object["name"] == "Luxord" and new_boss == "Luxord (Data)":
                return "Luxord" # There is a strange crash on Luxord Datas DM in original Luxords arena

            return new_boss
    
    @staticmethod
    def get_new_enemy(rand_seed, old_enemy_object, room, existing_bosses_as_enemies=0):
        if rand_seed.config.selected_enemy:
            new_enemy = rand_seed.config.selected_enemy
        elif rand_seed.config.enemymode == "Wild":
            new_enemy = pick_enemy_to_replace(old_enemy_object, rand_seed.config.enemies, rand_seed.wild_enemy_set, max_enemies=5)
        elif rand_seed.enemymapping:
            if old_enemy_object["name"] not in rand_seed.enemymapping:
                return old_enemy_object["name"] # if it's not in mapping it's not enabled so randomize it to itself
            new_enemy = rand_seed.enemymapping[old_enemy_object["name"]]
        if rand_seed.config.bosses_replace_enemies and rand_seed.config.bosses and not room.get("bossenemy_ignored"):            
            chance = 0.012
            if existing_bosses_as_enemies < 1 and random.random() < chance:
                # TODO this list doesn't need to be generated every time
                if not rand_seed.config.boss_enemies:
                    for boss_name in rand_seed.config.bosses:
                        boss = rand_seed.config.bosses[boss_name]
                        if boss["enabled"] and boss["can_be_enemy"]:
                            rand_seed.config.boss_enemies.append(boss_name)
                    for boss_name in rand_seed.config.boss_as_enemy_overrides:
                        rand_seed.config.boss_enemies.append(boss_name)
                new_enemy = random.choice(rand_seed.config.boss_enemies)
        return new_enemy

    @staticmethod
    def getSpId(spawnpoint, idnum):
        for spid in spawnpoint:
            if spid["Id"] == idnum:
                return spid
        raise Exception("Spid not found!")

    @staticmethod
    def getNewUnit(defaults):
        unit = {
            "Type": 1,
            "Flag": 0,
            "Id": 26,
            "Unk20": 0,
            "Unk24": 0,
            "Entities": [],
            "EventActivators": [],
            "WalkPath": [],
            "ReturnParameters": [],
            "Signals": [],
            "Teleport": {
                "Place": 0,
                "Door": 0,
                "World": 0,
                "Unknown": 0
            }
        }
        for k,v in defaults.items():
            unit[k] = v
        return unit