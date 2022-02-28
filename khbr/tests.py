import unittest, os, functools, sys, traceback, pdb
from khbr.randomizer import Randomizer, KingdomHearts2
from khbr.KH2.ModWriter import ModWriter
from khbr.randutils import pickbossmapping
import testutils
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
        r = Randomizer(tempdir=testutils.get_tmp_path())
        fn, rmdir = r._make_tmpdir()
        assert os.path.isdir(fn)
        rmdir()
        assert not os.path.exists(fn)
    
    def test_read_all_zexion(self):
        seedfn = os.path.join(os.path.dirname(__file__), "KH2", "data", "testdata", "zexion.json")
        if os.path.exists(os.path.join(testutils.get_tmp_path(), "test")):
            shutil.rmtree(os.path.join(testutils.get_tmp_path(), "test"))
        rando = Randomizer(tempdir=testutils.get_tmp_path(), tempfn="test")
        b64 = rando.read_seed("kh2", seedfn=seedfn)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_all_xemnas(self):
        options = {"selected_boss": "Xemnas"}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_one_one(self):
        options = {"boss": "One to One"}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_seedgen_boss_and_enemy_one_to_one(self):
        options = {"enemy": "One to One", "boss": "One to One"}
        randomization1 = testutils.generateSeed(options)
        randomization2 = testutils.generateSeed(options)
        randomization3 = testutils.generateSeed(options, seed="6789")
        assert randomization1 == randomization2
        assert randomization1 != randomization3
        testutils.validate_bosses_general(randomization1)
        testutils.validate_enemies_general(randomization1)

    def test_seedgen_enemy_one_to_one(self):
        options = {"enemy": "One to One"}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)

    def test_seedgen_enemy_one_to_one_pc(self):
        options = {"enemy": "One to One"}
        randomization = testutils.generateSeed(options)
        options["memory_expansion"] = True
        randomization_pc = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization_pc)
        assert randomization != randomization_pc 

    def test_seedgen_enemy_one_to_one_nightmare(self):
        options = {"enemy": "One to One", "nightmare_enemies": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)
        assert False == testutils.get_found(randomization, "Shadow")
        
    def test_seedgen_enemy_one_to_one_room(self):
        options = {"enemy": "One to One Per Room"}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general_perroom(randomization)

    def test_seedgen_enemy_one_to_one_room_nightmare(self):
        options = {"enemy": "One to One Per Room", "nightmare_enemies": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general_perroom(randomization)
        assert False == testutils.get_found(randomization, "Shadow")

    def test_seedgen_enemy_selected(self):
        options = {"selected_enemy": "Shadow WI"}
        randomization = testutils.generateSeed(options)
        testutils.validate_selected(randomization, "Shadow WI", isboss=False)

    def test_seedgen_boss_selected(self):
        options = {"selected_boss": "Xemnas"}
        randomization = testutils.generateSeed(options)
        print("Selected Boss")
        testutils.validate_selected(randomization, "Xemnas", isboss=True)

    def test_seedgen_boss_mickey_rule(self):
        options = {"boss": "One to One", "mickey_rule": "all"}
        randomization = testutils.generateSeed(options)
        for key, value in randomization["msn_map"].items():
            assert value["setmickey"] == True
        options = {"boss": "One to One", "mickey_rule": "none"}
        randomization = testutils.generateSeed(options)
        for key, value in randomization["msn_map"].items():
            assert value["setmickey"] == False
        options = {"boss": "One to One", "mickey_rule": "stay"}
        randomization = testutils.generateSeed(options)
        assert randomization["msn_map"]["BB05_MS104B"]["setmickey"] == True # Dark Thorn
        assert randomization["msn_map"]["CA01_MS204"]["setmickey"] == False # GR 2
        assert randomization["msn_map"]["CA18_MS202"]["setmickey"] == True # GR 1
        options = {"boss": "One to One", "mickey_rule": "follow"}
        randomization = testutils.generateSeed(options)
        # Technically should still test if the old locations get mickey disabled properly
        # But it requires knowing if the boss thats there would have mickey or not
        for old, new_object in randomization["msn_map"].items():
            if new_object["name"] == "BB05_MS104B":
                assert new_object["setmickey"] == True     
            if new_object["name"] == "CA01_MS204":
                assert new_object["setmickey"] == False
            if new_object["name"] == "CA18_MS202":
                assert new_object["setmickey"] == True   

    def test_seedgen_boss_one_to_one(self):
        options = {"boss": "One to One"}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        testutils.validate_bosses_onetoone(randomization)
        assert False == testutils.get_found(randomization, tags=["data", "cups"])

    def test_seedgen_boss_one_to_one_pc(self):
        options = {"boss": "One to One"}
        randomization = testutils.generateSeed(options)
        options["memory_expansion"] = True
        randomization_pc = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization_pc, pc=True)
        testutils.validate_bosses_onetoone(randomization_pc, pc=True)
        assert False == testutils.get_found(randomization_pc, tags=["data", "cups"])
        assert randomization_pc != randomization

    def test_seedgen_boss_one_to_one_scaled(self):
        options = {"boss": "One to One", "scale_boss_stats": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        testutils.validate_scale_map(randomization)

    def test_seedgen_boss_one_to_one_cups(self):
        options = {"boss": "One to One", "cups_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        

    def test_seedgen_boss_one_to_one_datas(self):
        options = {"boss": "One to One", "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_one_to_one_cups_datas(self):
        options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["data", "cups"])

    def test_seedgen_boss_wild(self):
        options = {"boss": "Wild"}
        randomization = testutils.generateSeed(options)
        print("Wild")
        print(randomization)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_randomized(randomization, "Final Xemnas")
        assert False == testutils.get_randomized(randomization, "Jafar")
        assert False == testutils.get_found(randomization, tags=["data", "cups"])

    def test_seedgen_boss_wild_cups(self):
        options = {"boss": "Wild", "cups_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        assert False == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_wild_datas(self):
        options = {"boss": "Wild", "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert False == testutils.get_found(randomization, tags=["cups"])
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_wild_cups_datas(self):
        options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_wild_nightmare(self):
        options = {"boss": "Wild", "nightmare_bosses": True}
        randomization = testutils.generateSeed(options)
        print("Nightmare")
        print(randomization) 
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_proderror1(self):
        options = {'boss': 'One to One', 'nightmare_bosses': False, 'selected_boss': None, 'enemy': 'One to One', 'selected_enemy': None, 'nightmare_enemies': False, 'scale_boss_stats': False, 'cups_bosses': False, 'data_bosses': False, 'memory_expansion': False}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)

    def test_seedgen_error2(self):
        options = {'boss': 'One to One', 'nightmare_bosses': False, 'selected_boss': None, 'enemy': 'Disabled', 'selected_enemy': None, 'nightmare_enemies': False, 'scale_boss_stats': True, 'cups_bosses': True, 'data_bosses': False, 'remove_damage_cap': False, 'memory_expansion': False}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_getbosses(self):
        kh2 = KingdomHearts2()
        kh2.enemy_manager.create_enemy_records(getavail=True)
        testutils.validate_enemy_records(kh2.enemy_manager.enemy_records)

    def test_enmp(self):
        import yaml
        kh2 = KingdomHearts2()
        with open(os.path.join(os.path.dirname(__file__), "KH2", "data", "enmpVanilla.yml")) as f:
            enmp_data_vanilla = yaml.load(f, Loader=yaml.SafeLoader)
        generated_enmp = ModWriter('.').enmp_manager.dumpEnmpData(enmp_data_vanilla)

    def test_pickbossmapping(self):
        kh2 = KingdomHearts2()
        bosses = kh2.enemy_manager.get_boss_list({})
        mapping = pickbossmapping(kh2.enemy_manager.enemy_records, bosses)
        def getcounts(mapping):
            counts = {}
            maxcounts = 0
            for old, new in mapping.items():
                if new not in counts:
                    counts[new] = 0
                if old not in counts:
                    counts[old] = 0
                counts[new] += 1
            return counts
        counted = getcounts(mapping)
        assert min(counted.values()) == 1
        assert max(counted.values()) == 1

    def validate_memory_expansion(self):
        options = {"enemy": "One to One Per Room", "memory_expansion": True}
        randomization_pc = testutils.generateSeed(options)
        options["memory_expansion"] = False
        randomization_ps2 = testutils.generateSeed(options)
        assert True == testutils.get_room_randomized(randomization_pc, "Agrabah", "The Cave of Wonders: Treasure Room", "b_40")
        assert False == testutils.get_room_randomized(randomization_ps2, "Agrabah", "The Cave of Wonders: Treasure Room", "b_40")

    def test_is_replacement_blocked(self):
        kh2 = KingdomHearts2()
        from khbr.KH2.schemas.enemy_records import get_schema
        source = get_schema()
        source["tags"] = ["rc_blocked"]
        dest = get_schema()
        assert not kh2.enemy_manager.isReplacementBlocked(source, dest)
        dest["tags"] = ["needs_rc"]
        assert kh2.enemy_manager.isReplacementBlocked(source, dest)


# Uncomment to run a single test through ipython
ut = Tests()
ut.test_seedgen_boss_one_to_one_scaled()

# Uncomment to run the actual tests
#unittest.main()
