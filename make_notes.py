from khbr.randomizer import KingdomHearts2
import random, os, json, time, string


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



start_time = time.time()

kh2 = KingdomHearts2()
bosses = kh2.get_bosses(usefilters=["boss"])
boss_names = sorted(bosses)
sources = []

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
    sources.append(source_boss_compatability)


boss_lines = [[""]+[s[0] for s in sources]]+sources

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


print(f"Data made: {time.time()-start_time}")
import sys; sys.stdout.flush()

import pygsheets
gc = pygsheets.authorize()
# gc.set_batch_mode(True)

print(f"Authorized: {time.time()-start_time}")
sys.stdout.flush()

sheet = gc.open("KH2 Enemy/Boss Randomizer Notes")

print(f"Sheet opened: {time.time()-start_time}")
sys.stdout.flush()

boss_sheet=sheet[2]


red = (1, 0, 0, 0)
green = (0.5, 1, 0, 0)

for row_index in range(len(boss_lines)):
    row = boss_lines[row_index]
    print(len(row))
    for col_index in range(len(row)):
        value = row[col_index]
        cell = boss_sheet.cell((row_index+1, col_index+1))
        if cell.value == value:
            continue # No change needed
        cell.value = value
        if value in ['X', 'O']:
            cell.color = green if value == 'O' else red
        cell.update()

print(f"Boss rows updated: {time.time()-start_time}")
sys.stdout.flush()

enemy_sheet = sheet[1]

for l in range(len(lines)):
    enemy_sheet.update_row(l+1, lines[l])

for i in title_rows:
    enemy_sheet.cell((i, 1)).set_text_format('bold', True).set_text_format('fontSize', 20)

print(f"Enemy rows updated: {time.time()-start_time}")
sys.stdout.flush()

boss_sheet_nightmare=sheet[4]


red = (1, 0, 0, 0)
green = (0.5, 1, 0, 0)

for row_index in range(len(bosslines_nightmare)):
    row = bosslines_nightmare[row_index]
    print(len(row))
    for col_index in range(len(row)):
        value = row[col_index]
        cell = boss_sheet_nightmare.cell((row_index+1, col_index+1))
        cell.value = value
        if value in ['X', 'O']:
            cell.color = green if value == 'O' else red
        cell.update()


print(f"Nightmare Boss rows updated: {time.time()-start_time}")
sys.stdout.flush()

enemy_sheet_nightmare = sheet[3]

for l in range(len(lines_nightmare)):
    enemy_sheet_nightmare.update_row(l+1, lines_nightmare[l])

for i in title_rows:
    enemy_sheet_nightmare.cell((i, 1)).set_text_format('bold', True).set_text_format('fontSize', 20)

print(f"NightmareEnemy rows updated: {time.time()-start_time}")
sys.stdout.flush()

# gc.run_batch()

print("All Done")
import sys; sys.stdout.flush()