import unittest
from randomizer import Randomizer

class Tests(unittest.TestCase):
    def test_valid_options(self):
        seed = "12345"
        game = "kh2"
        options = {
            "selected_enemy": "Air Pirate"
        }
        Randomizer()._validate_options(Randomizer()._get_game(game).get_options(), options)

    def test_filename_generate_expand(self):
        seed = "12345"
        game = "kh2"
        options = {
            "selected_enemy": "Air Pirate"
        }
        fn = Randomizer().generate_filename(game, seed, options)

        newgame, newseed, newoptions = Randomizer().expand_filename(fn)
        assert newgame == game
        assert newseed == seed
        assert newoptions == options


unittest.main()