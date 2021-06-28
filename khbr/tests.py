import unittest, os, functools, sys, traceback, pdb
from randomizer import Randomizer, KingdomHearts2
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
        seedfn = os.path.join(os.path.dirname(__file__), "testdata", "zexion.json")
        if os.path.exists(os.path.join(testutils.get_tmp_path(), "test")):
            shutil.rmtree(os.path.join(testutils.get_tmp_path(), "test"))
        rando = Randomizer(tempdir=testutils.get_tmp_path(), tempfn="test")
        b64 = rando.read_seed("kh2", seedfn=seedfn)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_all_xemnas(self):
        options = {"selected_boss": "Xemnas", "boss": "Selected Boss"}
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
        # Validate shadows outside tower are same as shadows outside enemy

    def test_seedgen_enemy_one_to_one_nightmare(self):
        options = {"enemy": "One to One", "nightmare_enemies": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)
        #validate shadows are not found anywhere and shadows outside tower are same as star room shadows

    def test_seedgen_enemy_one_to_one_room(self):
        options = {"enemy": "One to One Per Room"}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)
        # Validate all shadows outside tower are same
        # but in star tower they are all same but different

    def test_seedgen_enemy_one_to_one_room_nightmare(self):
        options = {"enemy": "One to One Per Room", "nightmare_enemies": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)
        # Validate no shadows exist
        # but in star tower they are different than outside

    def test_seedgen_enemy_selected(self):
        options = {"enemy": "Selected Enemy", "selected_enemy": "Shadow WI"}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)
        # Validate all enemies are shadow wi

    def test_seedgen_boss_selected(self):
        options = {"boss": "Selected Boss", "selected_boss": "Xemnas"}
        randomization = testutils.generateSeed(options)
        print("Selected Boss")
        print(randomization)
        # Validate all enemies are xemnas

    def test_seedgen_boss_one_to_one(self):
        options = {"boss": "One to One"}
        randomization = testutils.generateSeed(options)
        print("One to One")
        print(randomization)
        testutils.validate_bosses_general(randomization)
        # Validate hades is the same boss in all locations
        # Validate Validate all the parent bosses are still present
        # Validate cups and superbosses were not randomized, and no datas present

    def test_seedgen_boss_one_to_one_scaled(self):
        options = {"boss": "One to One", "scale_boss_stats": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        # validate the scale map matches the randomization map

    def test_seedgen_boss_one_to_one_cups(self):
        options = {"boss": "One to One", "cups_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        # validate cups bosses are present

    def test_seedgen_boss_one_to_one_datas(self):
        options = {"boss": "One to One", "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        # validate datas are present

    def test_seedgen_boss_one_to_one_cups_datas(self):
        options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        # validate cups and datas are both present

    def test_seedgen_boss_wild(self):
        options = {"boss": "Wild"}
        randomization = testutils.generateSeed(options)
        print("Wild")
        print(randomization)
        testutils.validate_bosses_general(randomization)
        # validate cups/datas are off
        # validate those like FX are randomized, but Jafar isn't

    def test_seedgen_boss_wild_scaled(self):
        options = {"boss": "Wild", "scale_boss_stats": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        # validate scaling worked right

    def test_seedgen_boss_wild_cups(self):
        options = {"boss": "Wild", "cups_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        # validate datas are present

    def test_seedgen_boss_wild_datas(self):
        options = {"boss": "Wild", "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        # validate datas are present

    def test_seedgen_boss_wild_cups_datas(self):
        options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)

    def test_seedgen_boss_wild_nightmare(self):
        options = {"boss": "Wild", "nightmare_bosses": True}
        randomization = testutils.generateSeed(options)
        print("Nightmare")
        print(randomization) 
        testutils.validate_bosses_general(randomization)
        # validate no cups or datas

    def test_seedgen_boss_wild_nightmare_cups(self):
        options = {"boss": "Wild", "nightmare_bosses": True, "cups_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)

    def test_seedgen_boss_wild_nightmare_datas(self):
        options = {"boss": "Wild", "nightmare_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        
    def test_seedgen_boss_wild_nightmare_cups_datas(self):
        options = {"boss": "Wild", "nightmare_bosses": True, "cups_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)

    def test_seedgen_proderror1(self):
        options = {'boss': 'One to One', 'nightmare_bosses': False, 'selected_boss': None, 'enemy': 'One to One', 'selected_enemy': None, 'nightmare_enemies': False, 'scale_boss_stats': False, 'cups_bosses': False, 'data_bosses': False, 'memory_expansion': False}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)

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

    def test_pickbossmapping(self):
        kh2 = KingdomHearts2()
        bosses = kh2.get_boss_list({})
        mapping = kh2.pickbossmapping(bosses)
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


# Uncomment to run a single test through ipython
# ut = Tests()
# ut.test_wild_luxord_source()

# Uncomment to run the actual tests
unittest.main()

# memory expansion=true test for enemies, validate certain rooms were ignored/not ignored
