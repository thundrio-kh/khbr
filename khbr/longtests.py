import unittest, os, functools, sys, traceback, pdb
from randomizer import Randomizer, KingdomHearts2
import testutils
import shutil, yaml
# Not really formal unit tests, more like just some basic integration tests to make sure different combinations of options work

class Tests(unittest.TestCase):

    def test_one_to_one_long(self):
        print("One to One long")
        N = 100
        options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True}
        randomizations = []
        for _ in range(N):
            print("{}\{}".format(_,N))
            randomization = testutils.generateSeed(options, str(_))
            randomizations.append(randomization)
        testutils.calculate_boss_percentages(randomizations, requireSourceReplace=True)
        testutils.check_for_hyena_replacement(randomizations)
        # Storm rider for luxord is pretty common unfortunately
        testutils.calculate_luxord_replacement_variety(randomizations, 0.55)

    def test_wild_long(self):
        print("Wild long")
        N = 100
        options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True}
        randomizations = []
        for _ in range(N):
            print("{}\{}".format(_,N))
            randomization = testutils.generateSeed(options, str(_))
            randomizations.append(randomization)
        testutils.calculate_boss_percentages(randomizations, requireSourceReplace=False)
        testutils.calculate_luxord_replacement_variety(randomizations, 0.4)
        testutils.check_for_hyena_replacement(randomizations)

    def test_one_to_one_long_pc(self):
        print("One to One long pc")
        N = 100
        options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True, "memory_expansion": True}
        randomizations = []
        for _ in range(N):
            print("{}\{}".format(_,N))
            randomization = testutils.generateSeed(options, str(_))
            randomizations.append(randomization)
        testutils.calculate_boss_percentages(randomizations, requireSourceReplace=True, pc=True)
        testutils.check_for_hyena_replacement(randomizations)
        testutils.calculate_luxord_replacement_variety(randomizations, 0.25, pc=True)

    # def test_wild_long_pc(self):
    #     print("Wild long pc")
    #     N = 100
    #     options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True, "memory_expansion": True}
    #     randomizations = []
    #     for _ in range(N):
    #         print("{}\{}".format(_,N))
    #         randomization = testutils.generateSeed(options, str(_))
    #         randomizations.append(randomization)
    #     testutils.calculate_boss_percentages(randomizations, requireSourceReplace=False, pc=True)
    #     testutils.calculate_luxord_replacement_variety(randomizations, 0.4, pc=True)
    #     testutils.check_for_hyena_replacement(randomizations)


# Uncomment to run a single test through ipython
ut = Tests()
#ut.test_wild_long_pc()

# Uncomment to run the actual tests
unittest.main()

# memory expansion=true test for enemies, validate certain rooms were ignored/not ignored

# I think I'm going to want a lot of "analyze randomization" functions so I can easily test lots of things in each test