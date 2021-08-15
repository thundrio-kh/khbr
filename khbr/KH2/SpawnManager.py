

from khbr.randutils import pick_boss_to_replace, pick_enemy_to_replace


class SpawnManager:
    def __init__(self):
        self.spawns = None
        self.roommodedits = {
            "ax2_99": self.ax2_99,
            "ax2_40": self.ax2_40,
            "ax2_50": self.ax2_50,
            "stormrider_61": self.stormrider_61
        }

    def set_spawns(self):
        if not self.spawns:
            self.spawns = self.get_locations()

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

    @staticmethod
    def should_replace_enemy(old_enemy_object):
        if not old_enemy_object["source_replace_allowed"]:
            return False
        return True

    @staticmethod
    def should_replace_boss(old_boss, old_boss_parent, config, rand_sed):
        if old_boss["name"] in ["Final Xemnas (Clone)", "Final Xemnas (Clone) (Data)"]:
            return False # He gets removed later by subtracts, so don't replace
        if not old_boss["source_replace_allowed"] and old_boss["name"] != "Seifer (2)":
            return False
        if config.bossmode == "Wild" and "onetooneonly" in old_boss["tags"]:
            return False
        if old_boss_parent["name"] not in rand_seed.bossmapping:
            return False
        return True

    @staticmethod
    def get_new_boss(old_boss_object, old_boss_parent, config, rand_seed):
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
            new_boss = pick_boss_to_replace(bosspicklist)

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
        if rand_seed.selected_enemy:
            new_enemy = rand_seed.selected_enemy
        elif rand_seed.enemymapping:
            if old_enemy_object["name"] not in rand_seed.enemymapping:
                return None # if it's not in mapping it's not enabled
            new_enemy = rand_seed.enemymapping[old_enemy_object["name"]]
        elif rand_seed.config.enemymode == "Wild":
            #TODO pretty sure this is broken, but also not safe to run in the game anyway
            new_enemy = pick_enemy_to_replace(old_enemy_object, rand_seed.config.enemies)
        return new_enemy