import unittest, os, functools, sys, traceback, pdb
from randomizer import Randomizer, KingdomHearts2
import shutil
# Not really formal unit tests, more like just some basic integration tests to make sure different combinations of options work

class Tests(unittest.TestCase):
    def test_valid_options(self):
        game = "kh2"
        options = {
            "selected_boss": "Zexion"
        }
        Randomizer()._validate_options(Randomizer()._get_game(game).get_options(), options)

    def test_tmpdir_create_delete(self):
        r = Randomizer(tempdir=self._get_tmp_path())
        fn, rmdir = r._make_tmpdir()
        assert os.path.isdir(fn)
        rmdir()
        assert not os.path.exists(fn)
    
    def test_read_all_zexion(self):
        seedfn = os.path.join(os.path.dirname(__file__), "testdata", "zexion.json")
        if os.path.exists(os.path.join(self._get_tmp_path(), "test")):
            shutil.rmtree(os.path.join(self._get_tmp_path(), "test"))
        rando = Randomizer(tempdir=self._get_tmp_path(), tempfn="test")
        b64 = rando.read_seed("kh2", seedfn=seedfn)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_all_xemnas(self):
        options = {"selected_boss": "Xemnas", "boss": "Selected Boss"}
        rando = Randomizer(tempdir=self._get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_one_one(self):
        options = {"boss": "One to One"}
        rando = Randomizer(tempdir=self._get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def _get_tmp_path(self):
        return os.path.join(os.getcwd(), "tmp")

    def _generateSeed(self, options, seed="12345"):
        rando = Randomizer(tempfn="test")
        return rando.generate_seed("kh2", options, seed, randomization_only=True)

    def test_seedgen_boss_and_enemy_one_to_one(self):
        options = {"enemy": "One to One", "boss": "One to One"}
        randomization1 = self._generateSeed(options)
        randomization2 = self._generateSeed(options)
        randomization3 = self._generateSeed(options, seed="6789")
        assert randomization1 == randomization2
        assert randomization1 != randomization3
        self._validate_bosses_general(randomization1)
        self._validate_enemies_general(randomization1)

    def test_seedgen_enemy_one_to_one(self):
        options = {"enemy": "One to One"}
        randomization = self._generateSeed(options)
        self._validate_enemies(randomization)
        self._validate_enemies_general(randomization)
        # Validate shadows outside tower are same as shadows outside enemy

    def test_seedgen_enemy_one_to_one_nightmare(self):
        options = {"enemy": "One to One", "nightmare_enemies": True}
        randomization = self._generateSeed(options)
        self._validate_enemies_general(randomization)
        #validate shadows are not found anywhere and shadows outside tower are same as star room shadows

    def test_seedgen_enemy_one_to_one_room(self):
        options = {"enemy": "One to One Per Room"}
        randomization = self._generateSeed(options)
        self._validate_enemies_general(randomization)
        # Validate all shadows outside tower are same
        # but in star tower they are all same but different

    def test_seedgen_enemy_one_to_one_room_nightmare(self):
        options = {"enemy": "One to One Per Room", "nightmare_enemies": True}
        randomization = self._generateSeed(options)
        self._validate_enemies_general(randomization)
        # Validate no shadows exist
        # but in star tower they are different than outside

    def test_seedgen_enemy_selected(self):
        options = {"enemy": "Selected Enemy", "selected_enemy": "Shadow WI"}
        randomization = self._generateSeed(options)
        self._validate_enemies_general(randomization)
        # Validate all enemies are shadow wi

    def test_seedgen_boss_one_to_one(self):
        options = {"boss": "One to One"}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # Validate hades is the same boss in all locations
        # Validate Validate all the parent bosses are still present
        # Validate cups and superbosses were not randomized, and no datas present

    def test_seedgen_boss_one_to_one_scaled(self):
        options = {"boss": "One to One", "scale_boss_stats": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate the scale map matches the randomization map

    def test_seedgen_boss_one_to_one_cups(self):
        options = {"boss": "One to One", "cups_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate cups bosses are present

    def test_seedgen_boss_one_to_one_datas(self):
        options = {"boss": "One to One", "data_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate datas are present

    def test_seedgen_boss_one_to_one_cups_datas(self):
        options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate cups and datas are both present

    def test_seedgen_boss_wild(self):
        options = {"boss": "Wild"}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate cups/datas are off
        # validate those like FX are randomized, but Jafar isn't

    def test_seedgen_boss_wild_scaled(self):
        options = {"boss": "Wild", "scale_boss_stats": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate scaling worked right

    def test_seedgen_boss_wild_cups(self):
        options = {"boss": "Wild", "cups_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate datas are present

    def test_seedgen_boss_wild_datas(self):
        options = {"boss": "Wild", "data_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate datas are present

    def test_seedgen_boss_wild_cups_datas(self):
        options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)

    def test_seedgen_boss_wild_nightmare(self):
        options = {"boss": "Wild", "nightmare_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        # validate no cups or datas

    def test_seedgen_boss_wild_nightmare_cups(self):
        options = {"boss": "Wild", "nightmare_bosses": True, "cups_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)

    def test_seedgen_boss_wild_nightmare_datas(self):
        options = {"boss": "Wild", "nightmare_bosses": True, "data_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)
        
    def test_seedgen_boss_wild_nightmare_cups_datas(self):
        options = {"boss": "Wild", "nightmare_bosses": True, "cups_bosses": True, "data_bosses": True}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)

    def test_seedgen_proderror1(self):
        options = {'boss': 'One to One', 'nightmare_bosses': False, 'selected_boss': None, 'enemy': 'One to One', 'selected_enemy': None, 'nightmare_enemies': False, 'scale_boss_stats': False, 'cups_bosses': False, 'data_bosses': False, 'memory_expansion': False}
        randomization = self._generateSeed(options)
        self._validate_bosses_general(randomization)

    def test_getbosses(self):
        kh2 = KingdomHearts2()
        kh2.get_bosses(usefilters=False, getavail=True)
        # check avail is mostly set correctly
        # check children/variations set correctly (including variation attributes set to parent, etc)
        # check tags set properly

    def test_enmp(self):
        import yaml
        kh2 = KingdomHearts2()
        with open(os.path.join(os.path.dirname(__file__), "data", "enmpVanilla.yml")) as f:
            enmp_data_vanilla = yaml.load(f, Loader=yaml.SafeLoader)
        generated_enmp = kh2.dumpEnmpData(enmp_data_vanilla)

    def test_boss_mapper(self):
        pass

    def _validate_nameforreplace(self, randomization):
        undercroft = randomization["spawns"]["Beast's Castle"]["Undercroft"]["spawnpoints"]["b_40"]
        enemies_used = set([e["name"] for e in undercroft["sp_ids"]["96"]])
        num_enemy_types = len(enemies_used)
        assert num_enemy_types == 1

    def _validate_enemies_general(self, randomization):
        self._validate_nameforreplace(randomization)

    def _validate_bosses_general(self, randomization):
        self._validate_boss_placements(randomization)

    def _validate_all_bosses_used(self, randomization):
        pass

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

# Uncomment to run the actual tests
unittest.main()

# Uncomment to run a single test through ipython
# ut = Tests()
# ut.test_seedgen_boss_and_enemy_one_to_one()

# memory expansion=true test for enemies, validate certain rooms were ignored/not ignored

# I think I'm going to want a lot of "analyze randomization" functions so I can easily test lots of things in each test