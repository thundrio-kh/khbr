from khbr.randomizer import KingdomHearts2
import random, os, json, time

# These bosses I'm not planning on ever randomizing, so can exclude them
exclusions = ["Banzai", "Barrel", "Demyx OC", "Ed", "Giant Sark", "MCP", "Hades Escape", "Jafar",
    "Lock", "Pete OC I", "Shenzie", "Shock", "Illuminator"]

# These enemies I'm not planning on ever randomizing, so they are excluded
# Bees
# Bulky Vendor
# Demyx's Water Clones
# Scar Ghost
# Vivi Clones
# Shadow Roxas
# Gambler (version that summons darkness)
# Illuminator

exclusions_enemies = []

kh2 = KingdomHearts2()

bosses = kh2.get_bosses(usefilters=["boss"])
boss_names = sorted(bosses)

bosslines = []

sources = []
names = []
for source_boss_name in boss_names:
    if source_boss_name in exclusions:
        continue
    source_boss = bosses[source_boss_name]
    if source_boss["parent"] != source_boss["name"]:
        continue
    source_boss_compatability = [source_boss_name]
    for new_boss_name in boss_names:
        if new_boss_name in exclusions:
            continue
        new_boss = bosses[new_boss_name]
        if new_boss["parent"] != new_boss["name"]:
            continue
    
        if new_boss["name"] in source_boss["available"]:
            compat = 'O'
        else:
            compat = 'X'
        
        source_boss_compatability.append(compat)
        names.append(new_boss_name)
    sources.append(source_boss_compatability)


bosslines.append([""]+sorted(set(names)))
bosslines += sources

with open("boss_compat.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in bosslines]))

bosslines_nightmare =[]

sources_nightmare = []
names_nightmare = []
for source_boss_name in boss_names:
    if source_boss_name in exclusions:
        continue
    source_boss = bosses[source_boss_name]
    if source_boss["parent"] != source_boss["name"]:
        continue
    source_boss_compatability = [source_boss_name]
    for new_boss_name in boss_names:
        if new_boss_name in exclusions:
            continue
        new_boss = bosses[new_boss_name]
        if not new_boss["isnightmare"]:
            continue
        if new_boss["parent"] != new_boss["name"]:
            continue
    
        if new_boss["name"] in source_boss["available"]:
            compat = 'O'
        else:
            compat = 'X'
        
        source_boss_compatability.append(compat)
        names_nightmare.append(new_boss_name)
    sources_nightmare.append(source_boss_compatability)

bosslines_nightmare.append([""]+sorted(set(names_nightmare)))
bosslines_nightmare += sources_nightmare

with open("boss_compat_nightmare.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in bosslines_nightmare]))

title_rows = []
lines = []
enemies = kh2.get_enemies()
enemies_dict = {}
for v in enemies:
    k = v["name"]
    enemies_dict[k] = v
categories = kh2.categorize_enemies(enemies)
for c in categories:
    lines.append([c])
    title_rows.append(len(lines))
    for e in sorted(categories[c]):
        enemy = enemies_dict[e]
        if enemy["name"] == enemy["parent"]:
            lines.append(sorted(enemy["children"]))

with open("enemy_cats.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in lines]))

title_rows_nightmare = []
lines_nightmare = []
enemies = kh2.get_enemies()
enemies_dict = {}
for v in enemies:
    k = v["name"]
    enemies_dict[k] = v
categories = kh2.categorize_enemies(enemies)
for c in categories:
    lines_nightmare.append([c])
    title_rows_nightmare.append(len(lines_nightmare))
    for e in sorted(categories[c]):
        enemy = enemies_dict[e]
        if enemy["name"] == enemy["parent"] and enemy["isnightmare"]:
            lines_nightmare.append(sorted(enemy["children"]))

with open("enemy_cats_nightmare.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in lines_nightmare]))