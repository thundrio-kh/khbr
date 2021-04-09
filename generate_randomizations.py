from khbr.randomizer import KingdomHearts2
import random, os, json

kh2 = KingdomHearts2()
bosses = kh2.get_bosses()

# Fake number right now
MAXCACHESIZE = 10_000_000_000_000_000_000
UNLIMITEDSIZE = 99_999_999_999_999
SOLUTIONSWANTED = 10

# A few bosses can be found in multiple spawnpoints, ignore the ones that don't matter
# to make a list of bosses with 1 spawnpoint each

outdir = os.path.join("khbr", "randomizations")
# Two option
for options in [{"name": "limited", "size": MAXCACHESIZE}, {"name": "unlimited", "size": UNLIMITEDSIZE},
            {"name": "limited-stable", "size": MAXCACHESIZE, "stableonly": True}, 
            {"name": "unlimited-stable", "size": UNLIMITEDSIZE, "stableonly": True}]:
    stableonly = options["stableonly"] if "stableonly" in options else False
    bosses = kh2.get_bosses(maxsize=options["size"], stable_only=stableonly)
    
    bosses_base = list(bosses.keys())

    solutions = []
    while len(solutions) < SOLUTIONSWANTED:
        possible_solution = list(bosses_base)
        random.shuffle(possible_solution)
    
        solution_found = True
        for b in range(len(possible_solution)):
            if not possible_solution[b] in bosses[bosses_base[b]]["available"]:
                solution_found = False
                break
        
        if solution_found:
            print(solution_found, len(solutions))
            solutions.append({bosses_base[i]:possible_solution[i] for i in range(len(possible_solution))})    

    for i in range(len(solutions)):
        fn = os.path.join(outdir, options["name"], str(i))
        if not os.path.isdir(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))
        json.dump(solutions[i], open(fn, "w"))