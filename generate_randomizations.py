from khbr.randomizer import KingdomHearts2
import random, os, json

kh2 = KingdomHearts2()
bosses = kh2.get_bosses()
locations = kh2.get_locations()

# Fake number right now
MAXCACHESIZE = 8_500_000_0
SOLUTIONSWANTED = 10

# A few bosses can be found in multiple spawnpoints, ignore the ones that don't matter
# to make a list of bosses with 1 spawnpoint each

for w in locations:
    world = locations[w]
    for r in world:
        room = world[r]
        for sp in room["spawnpoints"]:
            spawnpoint = room["spawnpoints"][sp]
            for spid in spawnpoint["sp_ids"].values():
                for ent in spid:
                    if ent["isboss"]:
                        if ent["name"] in bosses:
                            bosses[ent["name"]]["room_size"] = room["size"]
        

outdir = os.path.join("khbr", "randomizations")
# Two option
for maxsize in [{"name": "limited", "size": MAXCACHESIZE}, {"name": "unlimited", "size": 99_999_999_999_999}]:
    for b in bosses:
        boss = bosses[b]
        avail = []
        for bc in bosses:
            boss_check = bosses[bc]
            if "blacklist" in boss:
                if bc in boss["blacklist"]:
                    continue
            if "whitelist" in boss:
                if bc not in boss["whitelist"]:
                    continue
            if boss["size"] + boss_check["room_size"] >= maxsize["size"]:
                continue
            avail.append(boss_check["name"])
        boss["available"] = avail
    
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
        print(solution_found, len(solutions))
        if solution_found:
            solutions.append({bosses_base[i]:possible_solution[i] for i in range(len(possible_solution))})    

    for i in range(len(solutions)):
        fn = os.path.join(outdir, maxsize["name"], str(i))
        json.dump(solutions[i], open(fn, "w"))