from khbr.randomizer import KingdomHearts2

import time
starttime = time.time()

print("Initing obj")
kh2 = KingdomHearts2()
print("Took {}s".format(time.time()-starttime))

print("making records")
starttime = time.time()
full_records = kh2.get_bosses(usefilters=False, getavail=True)
print("Took {}s".format(time.time()-starttime))

import json, os

json.dump(full_records, open(os.path.join("khbr", "full_enemy_records.json"), "w"), indent=4)