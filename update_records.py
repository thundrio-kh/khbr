from khbr.randomizer import KingdomHearts2

import time, sys
starttime = time.time()

ispc = "pc" in sys.argv

print("Initing obj")
kh2 = KingdomHearts2()
print("Took {}s".format(time.time()-starttime))

print("making records")
starttime = time.time()
full_records = kh2.enemy_manager.create_enemy_records(ispc=ispc)

print("Took {}s".format(time.time()-starttime))

import json, os

name = "full_enemy_records.json" if not ispc else "full_enemy_records_pc.json"
json.dump(full_records, open(os.path.join("khbr", "KH2", "data", name), "w"), indent=4)
