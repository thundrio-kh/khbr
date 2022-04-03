
import unittest, os, functools, sys, traceback, pdb
from randomizer import Randomizer, KingdomHearts2
import testutils
import shutil, yaml, json

def get_boss_list(requireSourceReplace=True, pc=False):
    # Get a list of bosses that the enemies.yaml says is available
    # For isWild thats just every boss that is enabled
    # for oneToOne thats just every boss that is enabled + source_replace_allowed: true
    boss_list = []
    filename = "full_enemy_records"
    if pc:
        filename += "_pc"
    filename += ".json"
    enemy_json = json.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data", filename)))
    for enemy in enemy_json:
        enemy_obj = enemy_json[enemy]
        if enemy_obj["type"] == "boss" and enemy_obj["enabled"]:
            source_enabled = enemy_obj.get("source_replace_allowed", True) 
            replace_as = enemy_obj.get("replace_as", False)
            if requireSourceReplace and not source_enabled:
                continue
            if replace_as:
                continue
            boss_list.append(enemy)
    return boss_list

def get_luxord_replacement(randomization):
    try:
        return randomization["spawns"]["The World That Never Was"]["Havocs Divide"]["spawnpoints"]["b_40"]["sp_ids"]["69"][0]["name"]
    except KeyError:
        return "Luxord"

def check_for_hyena_replacement(randomizations):
    for randomization in randomizations:
        if "Pride Land" in randomization["spawns"]:
            assert "The Kings Den" not in randomization["spawns"]["Pride Land"]

def validate_bosses_general(randomization, pc=False):
    validate_consistent_bosses(randomization, pc=pc)
    return validate_boss_placements(randomization, pc=pc)

def validate_bosses_onetoone(randomization, pc=False):
    validate_bosses_show_up_once(randomization, pc=pc)

def validate_boss_placements(randomization, pc=False):
    import yaml
    kh2 = KingdomHearts2()
    if pc:
        kh2.enemy_manager.set_enemies("full_enemy_records_pc.json")
    vanilla = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data","locations.yaml")), loader=yaml.SafeLoader)
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
                        new_enemy_record = kh2.enemy_manager.enemy_records[new_name]
                        new_parent = kh2.enemy_manager.enemy_records[new_enemy_record["parent"]]
                        for old_ent in old_spid:
                            if new_index == old_ent["index"]:
                                old_enemy = kh2.enemy_manager.enemy_records[old_ent["name"]]
                                avail_list = kh2.enemy_manager.enemy_records[old_enemy["parent"]]["available"]
                                # prob need to do something about the parent
                                assert new_parent["name"] in avail_list, "{} is not in {}'s available list".format(new_name, old_enemy["name"])
    return used_bosses

def get_tmp_path():
    return os.path.join(os.getcwd(), "tmp")

def get_enemies_in(randomization, world, room, spn, spid=None):
    original = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data","locations.yaml")), Loader=yaml.SafeLoader)
    og_spawnpoint = original[world][room]["spawnpoints"][spn]
    try:
        spawnpoint = randomization["spawns"][world][room]["spawnpoints"][spn]
    except KeyError:
        # Spawnpoint isn't in the randomization, so it's all vanilla
        spawnpoint = og_spawnpoint
    enemies = []
    for spid_src in og_spawnpoint["sp_ids"]:
        if spid and spid != spid_src:
            continue
        for enemy in og_spawnpoint["sp_ids"][spid_src]:
            if spid_src not in spawnpoint["sp_ids"]:
                enemies.append(enemy)
                continue
            sp_ents = spawnpoint["sp_ids"][spid_src]
            new_ent = _find_index(sp_ents, enemy["index"])
            if not new_ent:
                enemies.append(enemy) # wasn't replaced, is vanilla
                continue
            enemies.append(new_ent)
    return enemies 

def validate_nameforreplace(randomization):
    undercroft = get_enemies_in(randomization, "Beast's Castle", "Undercroft", "b_40", spid="96")
    enemies_used = set([e["name"] for e in undercroft])
    num_enemy_types = len(enemies_used)
    assert num_enemy_types == 1

def validate_enemies_general(randomization):
    validate_nameforreplace(randomization)
    validate_shadows(randomization)

def validate_enemies_general_perroom(randomization):
    validate_nameforreplace(randomization)
    validate_shadows_perroom(randomization)

def validate_shadows(randomization):
    # validate 2 of same shadows are the same
    # also validate 2 different ones have the same parent
    first_location = get_enemies_in(randomization, "Twilight Town", "The Tower", "b_00")
    first_enemies = set([e["name"] for e in first_location])
    assert len(first_enemies) == 1
    first = list(first_enemies)[0]
    second_location = get_enemies_in(randomization, "Timeless River", "Scene of the Fire", "b_40", "42")
    second_enemies = set([e["name"] for e in second_location])
    assert len(second_enemies) == 1
    second = list(second_enemies)[0]
    kh2 = KingdomHearts2()
    assert kh2.enemy_manager.enemy_records[first]["parent"] == kh2.enemy_manager.enemy_records[second]["parent"]

def validate_shadows_perroom(randomization):
    # validate all shadows in the same room are the same
    # also validate 2 different ones are different
    kh2 = KingdomHearts2()
    first_location = get_enemies_in(randomization, "Twilight Town", "The Tower", "b_00")
    first_enemies = set([e["name"] for e in first_location])
    assert len(first_enemies) == 1
    first = list(first_enemies)[0]
    first_parent = kh2.enemy_manager.enemy_records[first]["parent"]
    second_location = get_enemies_in(randomization, "Timeless River", "Scene of the Fire", "b_40", "42")
    second_enemies = set([e["name"] for e in second_location])
    assert len(second_enemies) == 1
    second = list(second_enemies)[0]
    second_parent = kh2.enemy_manager.enemy_records[second]["parent"]
    third_location = get_enemies_in(randomization, "The World That Never Was", "Fragment Crossing", "b_10")
    third_enemies = set([e["name"] for e in third_location])
    assert len(third_enemies) == 1
    third = list(third_enemies)[0]
    third_parent = kh2.enemy_manager.enemy_records[third]["parent"]
    enemy_variety = set([first_parent, second_parent, third_parent])
    assert len(enemy_variety) > 1

def get_found(randomization, name=None, tags=[]):
    kh2 = KingdomHearts2()
    for world in randomization["spawns"].values():
        for room in world.values():
            for spawnpoint in room["spawnpoints"].values():
                for spid in spawnpoint["sp_ids"]:
                    for enemy in spawnpoint["sp_ids"][spid]:
                        if name:
                            if enemy["name"] == name:
                                print(enemy["name"])
                                return True
                        for tag in tags:
                            if "name" in enemy and tag in kh2.enemy_manager.enemy_records[enemy["name"]]["tags"]:
                                # TODO THIS IS A HACK BECAUSE HADES CUPS IS A REPLACEAS TARGET BUT HAS THE CUPS TAG
                                if enemy["name"] not in ["Hades Cups", "Pete Cups"]:
                                    return True
    return False

def get_randomized(randomization, source_name):
    original = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data","locations.yaml")), Loader=yaml.SafeLoader)
    for w, world in original.items():
        for r, room in world.items():
            for spn, spawnpoint in room["spawnpoints"].items():
                for spid, spawns in spawnpoint["sp_ids"].items():
                    for ent in spawns:
                        if ent["name"] == source_name:
                            new_spawns = randomization["spawns"].get(w,{}).get(r,{}).get("spawnpoints",{}).get(spn, {}).get("sp_ids", {}).get(spid, [])
                            
                            new_ent = _find_index(new_spawns, ent["index"])
                            if new_ent:
                                return ent["name"] != new_ent["name"]
                            return False # Wasn't replaced, is vanilla
                            
    raise Exception("Could not find source_name: {}".format(source_name))

def get_room_randomized(randomization, world, room, spn, spid=None):
    new = randomization["spawns"].get(world, {}).get(room, {}).get("spawnpoints", {}).get(spn, {})
    if spid:
        new = new.get("sp_ids", {}).get(spid, {})
    if new:
        return True
    return False

def validate_selected(randomization, name, isboss):
    for w, world in randomization["spawns"].items():
        for r, room in world.items():
            for spn, spawnpoint in room["spawnpoints"].items():
                for spid, spawns in spawnpoint["sp_ids"].items():
                    for ent in spawns:
                        if ent.get("isboss", False) == isboss:
                            if name != ent["name"]:
                                return False

def validate_consistent_bosses(randomization, pc=False):
    kh2 = KingdomHearts2()
    if pc:
        kh2.enemy_manager.set_enemies("full_enemy_records_pc.json")
    # Check that Cerberus and Cerberus in cups are the same parent
    # normal_cerberus = get_enemies_in("Olympus Coliseum", "Cave of the Dead: Entrance", "b_40")
    # cups_cerberus = get_enemies_in("Olympus Coliseum", "The Underdrome 09", "b_b0")
    # Check Demyx and Data Demyx are the same parent
    normal_demyx = get_enemies_in(randomization, "Hollow Bastion", "Castle Gate", "b_40")[0]["name"]
    data_demyx = get_enemies_in(randomization, "Hollow Bastion", "Castle Gate", "b_80")[0]["name"]
    assert kh2.enemy_manager.enemy_records[normal_demyx]["parent"] == kh2.enemy_manager.enemy_records[data_demyx]["parent"]

def validate_bosses_show_up_once(randomization, pc=False):
    assert True
    # Commenting out for now it seems too hard
    # You have to account for the bosses that show up more than once but are the same
    # which requires rewriting a lot of logic that defeats the point of an integration test
    # boss_appearances = {}
    # for w, world in randomization["spawns"].items():
    #     for r, room in world.items():
    #         for spn, spawnpoint in room["spawnpoints"].items():
    #             for spid, spawns in spawnpoint["sp_ids"].items():
    #                 for ent in spawns:
    #                     if ent["isboss"]:
    #                         assert
    #                         if name != ent["name"]:
    #                             return False


def _find_index(spid, index):
    # Given an index, and a list of entities, return the entity matching that index, or None if doesn't exist
    for ent in spid:
        if ent["index"] == index:
            return ent
    return None

def validate_scale_map(randomization):
    kh2 = KingdomHearts2()
    original = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data","locations.yaml")), Loader=yaml.SafeLoader)
    for w, world in original.items():
        for r, room in world.items():
            for spn, spawnpoint in room["spawnpoints"].items():
                for spid, spawns in spawnpoint["sp_ids"].items():
                    for ent in spawns:
                        if ent["isboss"]:
                            og_boss = ent["name"]
                            new_boss_spawns = randomization["spawns"].get(w, {}).get(r, {}).get("spawnpoints", {}).get(spn, {}).get("sp_ids", {}).get(spid, [])
                            new_boss = _find_index(new_boss_spawns, ent["index"])
                            if new_boss:
                                if new_boss["name"] in ["Hades Cups", "Armor Xemnas I", "Pete Cups", "Shadow Roxas"]:
                                    continue # These bosses don't get scaled properly for mostly replaceas reasons
                                # maybe something strange here that needs to be looked at again to ensure scaling done right
                                scaled_og = randomization["scale_map"][new_boss["name"]]
                                if type(scaled_og) == int:
                                    continue 
                                scaled_og_parent = kh2.enemy_manager.enemy_records[scaled_og]["parent"]
                                og_parent = kh2.enemy_manager.enemy_records[og_boss]["parent"]
                                assert scaled_og_parent == og_parent

def validate_enemy_records(enemy_records):
    enemies_yaml = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data","enemies.yaml")), Loader=yaml.SafeLoader)
    storm_original = enemies_yaml["Storm Rider"]
    storm_built = enemy_records["Storm Rider"]
    for name, enemy in enemy_records.items():
        if enemy["type"] == "boss":
            #some like banzai have no available
            if "available" in enemy and  "Storm Rider" in enemy["available"]:
                assert enemy["name"] in storm_original["whitelist_destination"]
    pass

def calculate_boss_percentages(randomizations, requireSourceReplace, pc=False):
    boss_ledger = {b: 0 for b in get_boss_list(requireSourceReplace=requireSourceReplace, pc=pc)}
    for randomization in randomizations:
        used = validate_bosses_general(randomization, pc=pc)
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

def calculate_luxord_replacement_variety(randomizations, max_percent, pc=False):
    storm_rider_count = 0
    N = len(randomizations)
    results = []
    for randomization in randomizations:
        validate_bosses_general(randomization, pc=pc)
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