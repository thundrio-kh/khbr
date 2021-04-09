import unittest, os, functools, sys, traceback, pdb
from randomizer import Randomizer
import shutil
# Not really formal unit tests, more like just some basic integration tests to make sure different combinations of options work

class Tests(unittest.TestCase):
    def test_valid_options(self):
        game = "kh2"
        options = {
            "selected_boss": "Zexion"
        }
        Randomizer()._validate_options(Randomizer()._get_game(game).get_options(), options)

# I don't think the filename is as important anymore don't need the test right now
    # def test_filename_generate_expand(self):
    #     seed = "12345"
    #     game = "kh2"
    #     options = {
    #         "selected_enemy": "Air Pirate"
    #     }
    #     fn = Randomizer().generate_filename(game, seed, options)

    #     newgame, newseed, newoptions = Randomizer().expand_filename(fn)
    #     assert newgame == game
    #     assert newseed == seed
    #     assert newoptions == options

    def test_tmpdir_create_delete(self):
        r = Randomizer(tempdir="/tmp")
        fn, rmdir = r._make_tmpdir()
        assert os.path.isdir(fn)
        rmdir()
        assert not os.path.exists(fn)
    
    def test_read_all_zexion(self):
        seedfn = os.path.join(os.path.dirname(__file__), "data", "zexion.seed")
        if os.path.exists(os.path.join("/tmp", "test")):
            shutil.rmtree(os.path.join("/tmp", "test"))
        rando = Randomizer(tempdir="/tmp", tempfn="test")
        b64 = rando.read_seed("kh2", seedfn=seedfn)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_all_xemnas(self):
        options = {"selected_boss": "Xemnas", "boss": "selected_boss"}
        rando = Randomizer(tempdir="/tmp")
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_one_one(self):
        options = {"boss": "one_to_one"}
        rando = Randomizer(tempdir="/tmp")
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_one_to_one_seedgen(self):
        options = {"boss": "one_to_one"}
        rando = Randomizer(tempfn="test")
        seed = "12345"
        randomization1 = rando.generate_seed("kh2", options, seed, randomization_only=True)
        randomization2 = rando.generate_seed("kh2", options, seed, randomization_only=True)
        assert randomization1 == randomization2

    def test_stable_one_to_one_seedgen(self):
        options = {"boss": "one_to_one", "stable_bosses_only": True}
        rando = Randomizer(tempfn="test")
        seed = "12345"
        rando.generate_seed("kh2", options, seed, randomization_only=True)

    def test_wild_seedgen(self):
        options = {"boss": "wild"}
        rando = Randomizer(tempfn="test")
        seed = "12345"
        rando.generate_seed("kh2", options, seed, randomization_only=True)
    
    def test_wild_nightmare_stable_seedgen(self):
        options = {"boss": "one_to_one", "nightmare_bosses": True}
        rando = Randomizer(tempfn="test")
        seed = "12345"
        randomization1 = rando.generate_seed("kh2", options, seed, randomization_only=True)
        randomization2 = rando.generate_seed("kh2", options, seed, randomization_only=True)

unittest.main()
