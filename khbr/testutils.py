
import unittest, os, functools, sys, traceback, pdb
from randomizer import Randomizer, KingdomHearts2
import testutils
import shutil, yaml

def get_boss_list(requireSourceReplace=True):
    # Get a list of bosses that the enemies.yaml says is available
    # For isWild thats just every boss that is enabled
    # for oneToOne thats just every boss that is enabled + source_replace_allowed: true
    boss_list = []
    enemy_yaml = yaml.load(open(os.path.join(os.path.dirname(__file__), "enemies.yaml")))
    for enemy in enemy_yaml.values():
        if enemy["type"] != "boss":
            continue
        for variation in enemy["variations"]:
            var_obj = enemy["variations"][variation]
            enabled = enemy.get("enabled", False) or var_obj.get("enabled", False)
            replace_as = enemy.get("replace_as", False) or var_obj.get("replace_as", False)
            source_enabled = enemy.get("source_replace_allowed", True) or var_obj.get("source_replace_allowed", False)
            if enabled and not replace_as:
                if requireSourceReplace:
                    if source_enabled:
                        boss_list.append(variation)
                    continue
                boss_list.append(variation)
    return boss_list

def get_luxord_replacement(randomization):
    try:
        return randomization["spawns"]["The World That Never Was"]["Havocs Divide"]["spawnpoints"]["b_40"]["sp_ids"]["69"][0]["name"]
    except KeyError:
        return "Luxord"

def validate_bosses_general(randomization):
    return validate_boss_placements(randomization)

def validate_boss_placements(randomization):
    import yaml
    kh2 = KingdomHearts2()
    vanilla = yaml.load(open("locations.yaml"))
    used_bosses = []
    for world_name in randomization["spawns"]:
        world = randomization["spawns"][world_name]
        for room_name in world:
            room = world[room_name]
            for spawnpoint_name in room["spawnpoints"]:
                spawnpoint = room["spawnpoints"][spawnpoint_name]
                for sp_id_name in spawnpoint["sp_ids"]:
                    spid = spawnpoint["sp_ids"][sp_id_name]
                    for e in range(len(spid)):
                        new_ent = spid[e]
                        if not new_ent.get("isboss"):
                            continue
                        old_spid = vanilla[world_name][room_name]["spawnpoints"][spawnpoint_name]["sp_ids"][sp_id_name] 
                        new_name = spid[e]["name"]
                        used_bosses.append(new_name)
                        # TODO handle checking these guys properly
                        # They aren't always in the old parents avail list, due to replaceAs nonsense
                        # but they are still their own parent
                        if new_name in ["Armor Xemnas I", "Armor Xemnas II", "Grim Reaper I", "Grim Reaper II", "Shadow Roxas"]:
                            continue
                        new_index = spid[e]["index"]
                        new_enemy_record = kh2.enemy_records[new_name]
                        new_parent = kh2.enemy_records[new_enemy_record["parent"]]
                        for old_ent in old_spid:
                            if new_index == old_ent["index"]:
                                old_enemy = kh2.enemy_records[old_ent["name"]]
                                avail_list = kh2.enemy_records[old_enemy["parent"]]["available"]
                                # prob need to do something about the parent
                                assert new_parent["name"] in avail_list, "{} is not in {}'s available list".format(new_name, old_enemy["name"])
    return used_bosses

def get_tmp_path():
    return os.path.join(os.getcwd(), "tmp")

def validate_nameforreplace(randomization):
    undercroft = randomization["spawns"]["Beast's Castle"]["Undercroft"]["spawnpoints"]["b_40"]
    enemies_used = set([e["name"] for e in undercroft["sp_ids"]["96"]])
    num_enemy_types = len(enemies_used)
    assert num_enemy_types == 1

def validate_enemies_general(randomization):
    validate_nameforreplace(randomization)

def calculate_boss_percentages(randomizations, requireSourceReplace):
    boss_ledger = {b: 0 for b in get_boss_list(requireSourceReplace=requireSourceReplace)}
    for randomization in randomizations:
        used = validate_bosses_general(randomization)
        for boss in boss_ledger:
            if boss in used:
                boss_ledger[boss] += 1
    print("Percentage boss placements")
    failed = 0
    for boss in sorted(boss_ledger, key=lambda b: boss_ledger[b]):
        if boss_ledger[boss] == 0:
            failed += 1
        print("{}: {}%".format(boss, round((boss_ledger[boss] / len(randomizations))*100, 2)))
    if failed:
        assert False, "{} bosses didn't get placed".format(failed)

def calculate_luxord_replacement_variety(randomizations, max_percent):
        storm_rider_count = 0
        N = len(randomizations)
        results = []
        for randomization in randomizations:
            validate_bosses_general(randomization)
            rep = get_luxord_replacement(randomization)
            if rep == "Storm Rider":
                storm_rider_count += 1
            results.append(rep)
        print("luxord replacements")
        print("Storm rider {} times".format(storm_rider_count))
        print(results)
        assert storm_rider_count <= N * max_percent

def generateSeed(options, seed="12345"):
    rando = Randomizer(tempfn="test")
    return rando.generate_seed("kh2", options, seed, randomization_only=True)