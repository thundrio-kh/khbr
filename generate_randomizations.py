from khbr.randomizer import KingdomHearts2
import random, os, json

kh2 = KingdomHearts2()
bosses = kh2.get_bosses()

# Fake number right now
MAXCACHESIZE = 10_000_000
SOLUTIONSWANTED = 10

# A few bosses can be found in multiple spawnpoints, ignore the ones that don't matter
# to make a list of bosses with 1 spawnpoint each

outdir = os.path.join("khbr", "randomizations")
# Two option
for maxsize in [{"name": "limited", "size": MAXCACHESIZE}, {"name": "unlimited", "size": 99_999_999_999_999}]:
    bosses = kh2.get_bosses(maxsize["size"])
    
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
        fn = os.path.join(outdir, maxsize["name"], str(i))
        json.dump(solutions[i], open(fn, "w"))