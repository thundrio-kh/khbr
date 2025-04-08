from khbr.randomizer import KingdomHearts2
import random, os, json, time

# These bosses I'm not planning on ever randomizing, so can exclude them
exclusions = ["Banzai", "Barrel", "Ed", "Giant Sark", "MCP",
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


######
##RUN FOR MOOSE
######
exclusions_enemies = []

kh2 = KingdomHearts2()
kh2.enemy_manager.set_enemies(moose=True)
records = kh2.enemy_manager.enemy_records

bosses = {b: records[b] for b in records if records[b]["type"] == "boss" and records[b]["name"] not in exclusions}
boss_names = sorted(bosses)

bosslines = []
allow_count = [0,0]
sources = []
names = []
for source_boss_name in boss_names:
    source_boss = bosses[source_boss_name]
    if source_boss["parent"] != source_boss["name"]:
        continue
    source_boss_compatability = [source_boss_name]
    for new_boss_name in boss_names:
        new_boss = bosses[new_boss_name]
        if new_boss["parent"] != new_boss["name"]:
            continue
    


        if new_boss["name"] in source_boss["available"]:
            source_room = None if not source_boss["msn"] else source_boss["msn"][:4]
            if source_room in new_boss["forced_variations"]:
                compat = 'F'
            else:
                compat = ''
            allow_count[0] += 1
            allow_count[1] += 1
        elif new_boss["name"] in source_boss["gimmick_source"]:
            compat = 'G'
            allow_count[0] += 1
            allow_count[1] += 1
        else:
            compat = 'X'
            allow_count[1] += 1

        source_boss_compatability.append(compat)
        names.append(new_boss_name)
    sources.append(source_boss_compatability)
print(f"MOOSE Boss Replacements: {allow_count[0]}/{allow_count[1]}")

bosslines.append(["Destination/Source"]+sorted(set(names)))
bosslines += sources

with open("boss_compat_moose.csv", "w") as f:
    # bosslines is a 2 dimensional list, where each row is a list of strings
    # reverse the x and y axis to make it easier to read
    f.write("\n".join([",".join(s) for s in zip(*bosslines)]))

bosslines_nightmare =[]
allow_count = [0,0]
sources_nightmare = []
names_nightmare = []
for source_boss_name in boss_names:
    source_boss = bosses[source_boss_name]
    if source_boss["parent"] != source_boss["name"]:
        continue
    source_boss_compatability = [source_boss_name]
    for new_boss_name in boss_names:
        new_boss = bosses[new_boss_name]
        if not new_boss["isnightmare"]:
            continue
        if new_boss["parent"] != new_boss["name"]:
            continue
    
        if new_boss["name"] in source_boss["available"]:
            source_room = None if not source_boss["msn"] else source_boss["msn"][:4]
            if source_room in new_boss["forced_variations"]:
                compat = 'F'
            else:
                compat = ''
            allow_count[0] += 1
            allow_count[1] += 1
        elif new_boss["name"] in source_boss["gimmick_source"]:
            compat = 'G'
            allow_count[0] += 1
            allow_count[1] += 1
        else:
            compat = 'X'
            allow_count[1] += 1
        
        source_boss_compatability.append(compat)
        names_nightmare.append(new_boss_name)
    sources_nightmare.append(source_boss_compatability)

print(f"MOOSE Nightmare Boss Replacements: {allow_count[0]}/{allow_count[1]}")

bosslines_nightmare.append(["Destination/Source"]+sorted(set(names_nightmare)))
bosslines_nightmare += sources_nightmare

with open("boss_compat_nightmare_moose.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in zip(*bosslines_nightmare)]))


# title_rows = []
# lines = []
# enemies = kh2.get_enemies()
# enemies_dict = {}
# for v in enemies:
#     k = v["name"]
#     enemies_dict[k] = v
# categories = kh2.categorize_enemies(enemies)
# for c in categories:
#     lines.append([c])
#     title_rows.append(len(lines))
#     for e in sorted(categories[c]):
#         enemy = enemies_dict[e]
#         if enemy["name"] == enemy["parent"]:
#             lines.append(sorted(enemy["children"]))

# with open("enemy_cats.csv", "w") as f:
#     f.write("\n".join([",".join(s) for s in lines]))

# title_rows_nightmare = []
# lines_nightmare = []
# enemies = kh2.get_enemies()
# enemies_dict = {}
# for v in enemies:
#     k = v["name"]
#     enemies_dict[k] = v
# categories = kh2.categorize_enemies(enemies)
# for c in categories:
#     lines_nightmare.append([c])
#     title_rows_nightmare.append(len(lines_nightmare))
#     for e in sorted(categories[c]):
#         enemy = enemies_dict[e]
#         if enemy["name"] == enemy["parent"] and enemy["isnightmare"]:
#             lines_nightmare.append(sorted(enemy["children"]))

# with open("enemy_cats_nightmare.csv", "w") as f:
#     f.write("\n".join([",".join(s) for s in lines_nightmare]))



######
##RUN FOR PS2
######
exclusions_enemies = []

kh2 = KingdomHearts2()
kh2.enemy_manager.set_enemies(moose=False)
records = kh2.enemy_manager.enemy_records

bosses = {b: records[b] for b in records if records[b]["type"] == "boss" and records[b]["name"] not in exclusions}
boss_names = sorted(bosses)

bosslines = []
allow_count = [0,0]
sources = []
names = []
for source_boss_name in boss_names:
    source_boss = bosses[source_boss_name]
    if source_boss["parent"] != source_boss["name"]:
        continue
    source_boss_compatability = [source_boss_name]
    for new_boss_name in boss_names:
        new_boss = bosses[new_boss_name]
        if new_boss["parent"] != new_boss["name"]:
            continue
    


        if new_boss["name"] in source_boss["available"]:
            source_room = None if not source_boss["msn"] else source_boss["msn"][:4]
            if source_room in new_boss["forced_variations"]:
                compat = 'F'
            else:
                compat = ''
            allow_count[0] += 1
            allow_count[1] += 1
        elif new_boss["name"] in source_boss["gimmick_source"]:
            compat = 'G'
            allow_count[0] += 1
            allow_count[1] += 1
        else:
            compat = 'X'
            allow_count[1] += 1

        source_boss_compatability.append(compat)
        names.append(new_boss_name)
    sources.append(source_boss_compatability)
print(f"PS2 Boss Replacements: {allow_count[0]}/{allow_count[1]}")

bosslines.append(["Destination/Source"]+sorted(set(names)))
bosslines += sources

with open("boss_compat_ps2.csv", "w") as f:
    # bosslines is a 2 dimensional list, where each row is a list of strings
    # reverse the x and y axis to make it easier to read
    f.write("\n".join([",".join(s) for s in zip(*bosslines)]))

bosslines_nightmare =[]
allow_count = [0,0]
sources_nightmare = []
names_nightmare = []
for source_boss_name in boss_names:
    source_boss = bosses[source_boss_name]
    if source_boss["parent"] != source_boss["name"]:
        continue
    source_boss_compatability = [source_boss_name]
    for new_boss_name in boss_names:
        new_boss = bosses[new_boss_name]
        if not new_boss["isnightmare"]:
            continue
        if new_boss["parent"] != new_boss["name"]:
            continue
    
        if new_boss["name"] in source_boss["available"]:
            source_room = None if not source_boss["msn"] else source_boss["msn"][:4]
            if source_room in new_boss["forced_variations"]:
                compat = 'F'
            else:
                compat = ''
            allow_count[0] += 1
            allow_count[1] += 1
        elif new_boss["name"] in source_boss["gimmick_source"]:
            compat = 'G'
            allow_count[0] += 1
            allow_count[1] += 1
        else:
            compat = 'X'
            allow_count[1] += 1
        
        source_boss_compatability.append(compat)
        names_nightmare.append(new_boss_name)
    sources_nightmare.append(source_boss_compatability)

print(f"PS2 Nightmare Boss Replacements: {allow_count[0]}/{allow_count[1]}")

bosslines_nightmare.append(["Destination/Source"]+sorted(set(names_nightmare)))
bosslines_nightmare += sources_nightmare

with open("boss_compat_nightmare_ps2.csv", "w") as f:
    f.write("\n".join([",".join(s) for s in zip(*bosslines_nightmare)]))


# title_rows = []
# lines = []
# enemies = kh2.get_enemies()
# enemies_dict = {}
# for v in enemies:
#     k = v["name"]
#     enemies_dict[k] = v
# categories = kh2.categorize_enemies(enemies)
# for c in categories:
#     lines.append([c])
#     title_rows.append(len(lines))
#     for e in sorted(categories[c]):
#         enemy = enemies_dict[e]
#         if enemy["name"] == enemy["parent"]:
#             lines.append(sorted(enemy["children"]))

# with open("enemy_cats.csv", "w") as f:
#     f.write("\n".join([",".join(s) for s in lines]))

# title_rows_nightmare = []
# lines_nightmare = []
# enemies = kh2.get_enemies()
# enemies_dict = {}
# for v in enemies:
#     k = v["name"]
#     enemies_dict[k] = v
# categories = kh2.categorize_enemies(enemies)
# for c in categories:
#     lines_nightmare.append([c])
#     title_rows_nightmare.append(len(lines_nightmare))
#     for e in sorted(categories[c]):
#         enemy = enemies_dict[e]
#         if enemy["name"] == enemy["parent"] and enemy["isnightmare"]:
#             lines_nightmare.append(sorted(enemy["children"]))

# with open("enemy_cats_nightmare.csv", "w") as f:
#     f.write("\n".join([",".join(s) for s in lines_nightmare]))