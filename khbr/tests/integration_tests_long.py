import testutils
# Not really formal unit tests, more like just some basic integration tests to make sure different combinations of options work

def test_one_to_one_long():
    print("One to One long")
    N = 100
    options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True, "gimmick_bosses": True, "sephiroth": True, "terra": True}
    randomizations = []
    for _ in range(N):
        print("{}\{}".format(_,N))
        randomization = testutils.generateSeed(options, str(_))
        randomizations.append(randomization)
    testutils.calculate_boss_percentages(randomizations, requireSourceReplace=True)
    testutils.check_for_hyena_replacement(randomizations)
    # Storm rider for luxord is pretty common unfortunately
    testutils.calculate_luxord_replacement_variety(randomizations, 0.55)

def test_wild_long():
    print("Wild long")
    N = 100
    options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True, "gimmick_bosses": True, "sephiroth": True, "terra": True}
    randomizations = []
    for _ in range(N):
        print("{}\{}".format(_,N))
        randomization = testutils.generateSeed(options, str(_))
        randomizations.append(randomization)
    testutils.calculate_boss_percentages(randomizations, requireSourceReplace=False)
    testutils.calculate_luxord_replacement_variety(randomizations, 0.4)
    testutils.check_for_hyena_replacement(randomizations)

def test_one_to_one_long_pc():
    print("One to One long pc")
    N = 100
    options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True, "gimmick_bosses": True, "sephiroth": True, "terra": True, "memory_expansion": True}
    randomizations = []
    for _ in range(N):
        print("{}\{}".format(_,N))
        randomization = testutils.generateSeed(options, str(_))
        randomizations.append(randomization)
    testutils.calculate_boss_percentages(randomizations, requireSourceReplace=True, pc=True)
    testutils.check_for_hyena_replacement(randomizations)
    testutils.calculate_luxord_replacement_variety(randomizations, 0.25, pc=True)

def test_wild_long_pc():
    print("Wild long pc")
    N = 100
    options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True, "gimmick_bosses": True, "sephiroth": True, "terra": True, "memory_expansion": True}
    randomizations = []
    for _ in range(N):
        print("{}\{}".format(_,N))
        randomization = testutils.generateSeed(options, str(_))
        randomizations.append(randomization)
    testutils.calculate_boss_percentages(randomizations, requireSourceReplace=False, pc=True)
    testutils.calculate_luxord_replacement_variety(randomizations, 0.4, pc=True)
    testutils.check_for_hyena_replacement(randomizations)

# need to add tests for can be enemy and can be enemy override

