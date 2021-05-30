from khbr.randomizer import KingdomHearts2
import random, os, json, time

kh2 = KingdomHearts2()
# TODO turn off filters
bosses = kh2.get_bosses()

sources = []

for source_boss_name in bosses:
    source_boss = bosses[source_boss_name]
    if source_boss["parent"] != source_boss["name"]:
        continue
    source_boss_compatability = [source_boss_name]
    for new_boss_name in bosses:
        new_boss = bosses[new_boss_name]
        if new_boss["parent"] != new_boss["name"]:
            continue
    
        if new_boss["name"] in source_boss["available"]:
            compat = 'O'
        else:
            compat = 'X'
        
        source_boss_compatability.append(compat)
    sources.append(source_boss_compatability)

lines = [[""]+[s[0] for s in sources]]+sources

with open("boss_compat.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in lines]))



lines = []
enemies = kh2.get_enemies()
enemies_dict = {}
for v in enemies:
    k = v["name"]
    enemies_dict[k] = v
categories = kh2.categorize_enemies(enemies)
for c in categories:
    lines.append([c])
    for e in categories[c]:
        enemy = enemies_dict[e]
        if enemy["name"] == enemy["parent"]:
            name = enemy["name"]
            children = "-".join(enemy["children"])
            lines.append([name,children])

with open("enemy_cats.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in lines]))