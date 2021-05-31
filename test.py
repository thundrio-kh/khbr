from khbr.randomizer import KingdomHearts2
import random, os, json, time

kh2 = KingdomHearts2()
bosses = kh2.get_bosses()


# Fake number right now
MAXCACHESIZE = 16.8#FAKE NUMBER # A little under Shan yu's max size, just a guess for right now
UNLIMITEDSIZE = 99_999_999_999_999
SOLUTIONSWANTED = 10

# A few bosses can be found in multiple spawnpoints, ignore the ones that don't matter
# to make a list of bosses with 1 spawnpoint each

outdir = os.path.join("khbr", "randomizations")
# Two option
options = {"name": "limited", "size": MAXCACHESIZE}

print(options)
bosses = kh2.get_bosses(maxsize=options["size"])
    
bosses_base = list(bosses.keys())

# Sort bosses according to their size
for boss in sorted(bosses, key=lambda k: bosses[k]["size"]):
    print("{}-{}".format(boss, bosses[boss]["size"]))