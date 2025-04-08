from khbr.randomizer import KingdomHearts2
import random
import json, os
random.seed(5)
import time, sys
starttime = time.time()

moose = "moose" in sys.argv

print("Initing obj")
kh2 = KingdomHearts2()
print(f"Took {time.time()-starttime}s")

print("making records")
starttime = time.time()
full_records = kh2.enemy_manager.create_enemy_records(moose=False)
name = "full_enemy_records.json"
json.dump(full_records, open(os.path.join("khbr", "KH2", "data", name), "w"), indent=4)
print("making MOOSE records")
full_records = kh2.enemy_manager.create_enemy_records(moose=True)

name = "full_enemy_records_moose.json"
json.dump(full_records, open(os.path.join("khbr", "KH2", "data", name), "w"), indent=4)
print(f"Took {time.time()-starttime}s")



