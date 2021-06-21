import unittest, os, functools, sys, traceback, pdb
from randomizer import Randomizer, KingdomHearts2
import shutil
# Not really formal unit tests, more like just some basic integration tests to make sure different combinations of options work

class Tests(unittest.TestCase):
    def _generateSeed(self, options, seed="12345"):
        rando = Randomizer(tempfn="test")
        return rando.generate_seed("kh2", options, seed, randomization_only=True)

    def test_one_to_one_luxord_source(self):
        print("One to One Luxord Test")
        options = {"boss": "One to One"}
        storm_rider_count = 0
        N = 100
        max_percent = 0.4
        results = []
        for _ in range(N):
            randomization = self._generateSeed(options, str(_))
            self._validate_bosses_general(randomization)
            rep = self._get_luxord_replacement(randomization)
            if rep == "Storm Rider":
                storm_rider_count += 1
            results.append(rep)
        print(results)
        assert storm_rider_count <= N * max_percent

    def test_wild_luxord_source(self):
        print("Wild Luxord Test")
        options = {"boss": "Wild"}
        storm_rider_count = 0
        N = 100
        max_percent = 0.4
        results = []
        for _ in range(N):
            randomization = self._generateSeed(options, str(_))
            self._validate_bosses_general(randomization)
            rep = self._get_luxord_replacement(randomization)
            if rep == "Storm Rider":
                storm_rider_count += 1
            results.append(rep)
        print(results)
        assert storm_rider_count <= N * max_percent

    def _get_luxord_replacement(self, randomization):
        try:
            return randomization["spawns"]["The World That Never Was"]["Havocs Divide"]["spawnpoints"]["b_40"]["sp_ids"]["69"][0]["name"]
        except KeyError:
            return "Luxord"

    def _validate_bosses_general(self, randomization):
        self._validate_boss_placements(randomization)

    def _validate_boss_placements(self, randomization):
        import yaml
        kh2 = KingdomHearts2()
        vanilla = yaml.load(open("locations.yaml"))
        for world_name in randomization["spawns"]:
            world = randomization["spawns"][world_name]
            for room_name in world:
                room = world[room_name]
                for spawnpoint_name in room["spawnpoints"]:
                    spawnpoint = room["spawnpoints"][spawnpoint_name]
                    for sp_id_name in spawnpoint["sp_ids"]:
                        spid = spawnpoint["sp_ids"][sp_id_name]
                        for e in range(len(spid)):
                            new_ent = spid[e]
                            if not new_ent.get("isboss"):
                                continue
                            old_spid = vanilla[world_name][room_name]["spawnpoints"][spawnpoint_name]["sp_ids"][sp_id_name] 
                            new_name = spid[e]["name"]
                            # TODO handle checking these guys properly
                            # They aren't always in the old parents avail list, due to replaceAs nonsense
                            # but they are still their own parent
                            if new_name in ["Armor Xemnas I", "Armor Xemnas II", "Grim Reaper I", "Grim Reaper II", "Shadow Roxas"]:
                                continue
                            new_index = spid[e]["index"]
                            new_enemy_record = kh2.enemy_records[new_name]
                            new_parent = kh2.enemy_records[new_enemy_record["parent"]]
                            for old_ent in old_spid:
                                if new_index == old_ent["index"]:
                                    old_enemy = kh2.enemy_records[old_ent["name"]]
                                    avail_list = kh2.enemy_records[old_enemy["parent"]]["available"]
                                    # prob need to do something about the parent
                                    assert new_parent["name"] in avail_list, "{} is not in {}'s available list".format(new_name, old_enemy["name"])


# Uncomment to run a single test through ipython
# ut = Tests()
# ut.test_wild_luxord_source()


# Uncomment to run the actual tests
unittest.main()

# memory expansion=true test for enemies, validate certain rooms were ignored/not ignored

# I think I'm going to want a lot of "analyze randomization" functions so I can easily test lots of things in each test