import time, json, random, os, shutil, yaml, base64, sys
from zipfile import ZipFile
import random

DEBUG_LOCATIONS = []

supported_games = ["kh2"]

diagnostics = True
GENERATE_IDENTICON = False

KH2_DIR = os.environ["USE_KH2_GITPATH"]
RANDOMIZATIONS_DIR = os.path.join(KH2_DIR,"randomizations") if os.path.exists(os.path.join(KH2_DIR,"randomizations")) else "randomizations"

UNLIMITED_SIZE = 99_999_999_999_999
LIMITED_SIZE = 15.0 # Seems about right
NUM_RANDOMIZATION_MAPPINGS = 9

HARDCAP = "-3.3895395E+38"

def final_fight_text(source_enemy, new_name):
    key = "{}-{}-{}".format(source_enemy["ObjectId"], source_enemy["Argument1"], source_enemy["Argument2"])
    texts = {
        "2079-1-0": { # Final Xemnas
            "id": 18453,
            "en": """{0} has problem grown even
stronger, and is waiting for us.{{:clear }}This battle began with Ansem's
research, Let´s finish it for him!"""},
        "2140-0-0": { # AX 2
            "id": 18456,
            "en": """Don´t let your guard down. 
{0} may separate us at any time.{{:clear }}Come on, let´s save the world again!"""},
        "2140-1-0": { # AX1
            "id": 18457,
            "en": """The Kingdom Hearts opened the door
to {0}.{{:clear }}We can´t let this chance slip by. It´s
going to be a tough fight, but we can do it!"""}
}
    if key not in texts:
        return ''
    text = dict(texts[key])
    text["en"] = text["en"].format(new_name)
    return text

def ax2_99(spawnpoint):
    # set the characters Y values and X values properly
    sora = spawnpoint[0]["Entities"][0]
    sora["PositionY"] = 14940
    # track for later
    bossz = float(sora["PositionZ"])
    sora["PositionZ"] = float(spawnpoint[0]["Entities"][2]["PositionZ"])

    riku = spawnpoint[0]["Entities"][1]
    riku["PositionY"] = 14940
    riku["PositionZ"] = float(spawnpoint[0]["Entities"][2]["PositionZ"])

    boss = spawnpoint[0]["Entities"][2]
    boss["PositionY"] = 14940
    boss["PositionZ"] = bossz
def ax2_40(spawnpoint):
    # remove the buildings
    for spid in spawnpoint:
        spid["Entities"] = []
def ax2_50(spawnpoint):
    # remove the dragon
    spawnpoint[0]["Entities"] = []

roommodedits = {
    "ax2_99": ax2_99,
    "ax2_40": ax2_40,
    "ax2_50": ax2_50
}

class AreaDataScript:
    def __init__(self, txt, ispc=False):
        self.script = txt
        self.ispc = ispc
        self.programs = self.parse_programs(self.script)
    def parse_programs(self, script):
        programs = {}
        currentProgram = None
        lines_program = []
        for line in script.split("\n"):
            if line.startswith("Program"):
                if currentProgram:
                    programs[currentProgram] = lines_program
                currentProgram = int(line.split(" ")[1], 16)
                lines_program = [line]
            else:
                lines_program.append(line)
        if currentProgram:
            programs[currentProgram] = lines_program
        return programs
    def get_program(self, number):
        if number not in self.programs:
            raise Exception("Program not found")
        return '\n'.join(self.programs[number])
    def update_program(self, number, capacity=None):
        program = self.get_program(number).split("\n")
        topop = []
        for l in range(len(program)):
            line = program[l]
            if capacity and "Capacity" in line:
                if self.ispc:
                    topop.append(l)
                    continue
                cap_line = line.split(" ")
                cap_line[1] = capacity
                program[l] = ' '.join(cap_line)
        if self.ispc:
            for p in topop[::-1]:
                program.pop(p)
        self.programs[number] = program
    def has_capacity(self, number):
        program = self.get_program(number)
        for line in program.split("\n"):
            if "Capacity" in line:
                return True
        return False
    def has_mission(self, number):
        program = self.get_program(number)
        for line in program.split("\n"):
            if "Mission" in line:
                return True
        return False
    def get_mission(self, number):
        if not self.has_mission(number):
            return None
        program = self.get_program(number)
        for line in program.split("\n"):
            if "Mission" in line:
                return line.split(" ")[-1]

class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "01"
        self.name = "kh2"
        self.unlimited_memory = False
        self.spawns = None
        with open(os.path.join(os.path.dirname(__file__), "location-ard-map.json")) as f:
            self.locmap = json.load(f)
        with open(os.path.join(os.path.dirname(__file__), "msns.json")) as f:
            self.msninfo = json.load(f)
        with open(os.path.join(os.path.dirname(__file__), "full_enemy_records.json")) as f:
            self.enemy_records = json.load(f)        
    def set_spawns(self):
        if not self.spawns:
            self.spawns = self.get_locations()
    def get_valid_enemies(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "enemy"]
    def get_valid_bosses(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "boss"]
    def get_options(self):
        # Might want to define valid predicates at some point, as certain combinations can't be selected together
        return {
            "enemy": {"display_name": "Enemy Randomization Mode", "description": "Select if and how the enemies should be randomized. Available choices: One-to-One replacement ie all shadows become dusks. One-to-One per room: One-to-One but every room is rerandomized (so shadows in Parlor might be ice cubes, but in LOD Cave they might be fire cubes). Wild: every enemy entity in the game is completely randomized",
                                  "possible_values": ["Disabled", "One to One", "One to One Per Room", "Selected Enemy"], "hidden_values": ["Wild"]},
            "selected_enemy": {"display_name": "Selected Enemy", "description": "Replaces every enemy with the selected enemy. Depending on the enemy may not generate a completable seed. This value is ignored if enemy randomization mode is not 'Selected Enemy'",
                                "possible_values": [None] + sorted(self.get_valid_enemies()), "hidden_values": []},
            # "bosses_can_replace_enemies": {"display_name": "Bosses Can Replace Enemies", "description": "Replaces a small percentage of enemies in the game with a random boss. This option is intended for PC use only.",
            #                     "possible_values": [False, True], "hidden_values": []},
            "nightmare_enemies": {"display_name": "Nightmare Enemies", "description": "Replaces enemies using only the most difficult enemies in the game.",
                                "possible_values": [False, True], "hidden_values": []},
            # "separate_small_big_enemies": {"display_name": "Separate Small and Big Enemies", "description": "Randomizes big enemies among themselves and small enemies among themselves. Useful to prevent crashing"},
            #                     "possible_values": [True, False], "hidden_values": []},
            # "scale_enemy_stats": {"display_name": "Scale Enemy Stats", "description": "Attempts to scale enemies to the level/HP of the enemy it is replacing.",
            #                     "possible_values": [True, False], "hidden_values": []},

            "memory_expansion": {"display_name": "Use Expanded Memory", "description": "The PS2 version of the game has more limited enemy randomization capabilities. Turn this option on if playing on PC to remove these constraints.",
                                "possible_values": [False, True], "hidden_values": []},

            "boss": {"display_name": "Boss Randomization Mode", "description": "Select if and how the bosses should be randomized. Available choices: One-to-One replacement just shuffles around where the bosses are located, but each boss is still present (some bosses may be excluded from the randomization). Wild will randomly pick an available boss for every location, meaning some bosses can be seen more than once, and some may never be seen. Selected Boss will replace every boss with a single selected boss.",
                                "possible_values": ["Disabled", "Wild", "Selected Boss"], "hidden_values": ["One to One"]},#, "one_to_one_characters",
            "selected_boss": {"display_name": "Selected Boss", "description": "Replaces every boss possible with the selected boss. Depending on the boss may not generate a completable seed. This value is ignored if boss mode is not 'Selected Boss'",
                                "possible_values": [None] + sorted(self.get_valid_bosses()), "hidden_values": []},
            "nightmare_bosses": {"display_name": "Nightmare Bosses", "description": "Replaces bosses using only the most difficult bosses in the game.",
                                "possible_values": [False, True], "hidden_values": []},
            "scale_boss_stats": {"display_name": "Scale Bosses", "description": "Attempts to scale bosses to the level/HP of the boss it is replacing.",
                                "possible_values": [True, False], "hidden_values": []},
            "cups_bosses": {"display_name": "Randomize Cups Bosses", "description": "Include the coliseum bosses in the randomization pool. In 'One for One', this will cause these bosses to be prett common, as there are 3-4 separate instances of most cups bosses.",
                                "possible_values": [True, False], "hidden_values": []},
            "data_bosses": {"display_name": "Randomize Superbosses", "description": "Include the Data versions of organization members in the pool, as well as Terra and Sephiroth",
                                "possible_values": [False, True], "hidden_values": []}
        }
    def get_enemies(self):
        enemies = self.get_valid_enemies()
        enabled_enemies = [self.enemy_records[e] for e in enemies if self.enemy_records[e]["enabled"]]
        return enabled_enemies
    def get_bosses(self, nightmare_mode=False, maxsize=LIMITED_SIZE, usefilters=["boss", "enabled", "nightmare"], getavail=True):
        defaults = {
            "replace_as": None,
            "source_replace_allowed": True,
            "model": None,
            "msn_replace_allowed": True,
            "tags": [],
            "cups": False,
            "data": False,
            "category": None,
            "level": 0,
            "isnightmare": False,
            "parent": None,
            "variationof": None,
            "children": [],
            "hp": 100,
            "limiter": 1,
            "msn_required": False,
            "msn_source_as": None,
            "aimod": None,
            "can_be_enemy": False,
            "msn": None,
            "size": 0,
            "sizeTag": None, #sizeSmall sizeMedium sizeLarge 
            "room_size": 0,
            "roommaxsize": None,
            "enmp_index": None,
            "variations": [],
            "enabled": True,
            "blacklist_source": [],
            "blacklist_destination": [],
            "whitelist_source": [],
            "whitelist_destination": [],
            "adds": [],
            "subtracts": [],
            "msn_list": [],
            "program": None,
            "roomsizemultiplier": 1,
            "unchanged_file_size": False,
            "obj_edits": {}
        }
        with open(os.path.join(os.path.dirname(__file__), "enemies.yaml")) as f:
            bosses_f = yaml.load(f, Loader=yaml.FullLoader)
        bosses = {}
        kidlist = {}
        for name in bosses_f:
            b = bosses_f[name]
            for v in b["variations"]:
                boss = dict(b["variations"][v])
                boss["name"] = v
                for k in b:
                    if k == "variations":
                        boss[k] = list(b[k].keys())
                        continue
                    if k not in boss:
                        boss[k] = b[k]
                for d in defaults:
                    if d not in boss:
                        boss[d] = defaults[d]
                boss["category"] = '-'.join(sorted(boss["tags"]))
                if boss["sizeTag"]:
                    boss["category"] = "-".join([boss["category"], boss["sizeTag"]])

                if len(boss["category"]) > 0 and boss["category"][0] == "-":
                    boss["category"] = boss["category"][1:]
                if usefilters:
                    if "boss" in usefilters and boss["type"] != 'boss':
                        continue
                    if "enabled" in usefilters and not boss['enabled']:
                        continue
                    if "nightmare" in usefilters and nightmare_mode and not ("isnightmare" in boss and boss["isnightmare"]):
                        continue

                parent = boss["variationof"] or name
                assert parent != None
                if not boss["parent"]:
                    boss["parent"] = parent
                if parent not in kidlist:
                    kidlist[parent] = []
                kidlist[parent].append(name)
                
                bosses[v] = boss
        
        for parent in kidlist:
            bosses[parent]["children"] = list(set(kidlist[parent]))

        if getavail:
            for source_name in bosses:
                source_boss = bosses[source_name]
                if not source_boss["type"] == "boss":
                    continue
                # Avail only needs to be filled in for the parent
                if not source_boss["parent"] == source_name:
                    continue
                avail = [] # These are bosses that are allowed to be here
                for dest_name in bosses:
                    dest_boss = bosses[dest_name]
                    if not dest_boss["type"] == "boss":
                        continue
                    if not dest_boss["parent"] == dest_name:
                        continue
                    if dest_boss["name"] == source_boss["name"]:
                        # Boss should always be allowed to be in it's own location
                        avail.append(dest_boss["name"])
                        continue
                    if not dest_boss["enabled"]:
                        continue
                    if source_boss["unchanged_file_size"] and (dest_boss["adds"] or dest_boss["subtracts"]):
                        continue
                    if not source_boss["source_replace_allowed"]:
                        continue
                    if dest_boss["blacklist_destination"]:
                        if source_name in dest_boss["blacklist_destination"]:
                            continue
                    if dest_boss["whitelist_destination"]:
                        if source_name not in dest_boss["whitelist_destination"]:
                            continue
                    if source_boss["blacklist_source"]:
                        if dest_name in source_boss["blacklist_source"]:
                            continue
                    if source_boss["whitelist_source"]:
                        if dest_name not in source_boss["whitelist_source"]:
                            continue
                    if not source_boss["msn_replace_allowed"]:
                        if dest_boss["msn_required"]:
                            continue
                    #print("{} > {}: {} + {} >= {}".format(source_boss["name"], dest_boss["name"], source_boss["size"], dest_boss["room_size"], maxsize))
                    # THIS NEEDS TO CHANGE ONCE I CAN DO UNLIMITED STUFF
                    roommaxsize = source_boss["roommaxsize"] or maxsize
                    availablespace = (roommaxsize - source_boss["room_size"]) * source_boss["roomsizemultiplier"]
                    #print("{} - {} ({}) >= 0".format(availablespace, source_boss["size"], availablespace - source_boss["size"]))
                    if availablespace - dest_boss["size"] < 0:
                        continue
                    avail.append(dest_boss["name"])
                source_boss["available"] = avail
        return bosses
    def get_locations(self):
        with open(os.path.join(os.path.dirname(__file__), "locations.yaml")) as f:
            locations_f = yaml.load(f, Loader=yaml.FullLoader)
        if DEBUG_LOCATIONS:
            newlocations = {}
            for world in locations_f:
                for room in locations_f[world]:
                    if room in DEBUG_LOCATIONS:
                        if world not in newlocations:
                            newlocations[world] = {}
                        newlocations[world][room] = locations_f[world][room]
            locations_f = newlocations
        return locations_f
    def add_tag(self, enemylist, tag):
        for enemy in enemylist:
            enemy["tags"].append(tag)
        return enemylist
    def remove_tag(self, enemylist, tag):
        for enemy in enemylist:
            enemy["tags"] = list(filter(lambda k: k != tag), enemylist)
    def pickbossmapping(self, bosslist, category):
        # Randomization with limitations can take a while, so pregenerate 100K randomizations for each option
        # then just pick one of the right type
        num_files = NUM_RANDOMIZATION_MAPPINGS
        dirname = os.path.join(RANDOMIZATIONS_DIR, category)
        num = random.randint(1,num_files)
        with open(os.path.join(dirname, str(num))) as f:
            return json.load(f)
    def categorize_enemies(self, enemylist):
        categories = {}
        for e in enemylist:
            parent = self.enemy_records[e["parent"]]
            # Might not be respecting childrens tags properly
            if parent["category"] not in categories:
                categories[parent["category"]] = {}
            categories[parent["category"]][parent["name"]] = parent
        return categories
    def pickenemymapping(self, enemylist):
        # Create separate lists for each set of tags used by enemies
        categories = self.categorize_enemies(enemylist)
        mapping = {}
        for c in categories:
            og = list(categories[c].values()) # Remove duplicate parent entries
            new = list(og)
            random.shuffle(new)
            for i in range(len(og)):
                old_parent = og[i]
                new_parent = new[i]
                # So for each child of the new_parent, randomly pick a child of the old_parent
                # Then go through the variations of each, and add them to the mapping
                for old_child_name in old_parent["children"]:
                    new_child_name = random.choice(new_parent["children"])
                    new_child = self.enemy_records[new_child_name]
                    old_child = self.enemy_records[old_child_name]
                    for old_variation_name in old_child["variations"]:
                        new_variation_name = random.choice(list(new_child["variations"]))
                        if old_variation_name in mapping:
                            raise Exception("TESTCHECK, something is getting incorrectly overwritten")
                        mapping[old_variation_name] = new_variation_name
        enemylistnames = [e["name"] for e in enemylist]
        assert len(enemylist) == len(list(mapping.keys()))
        
        return mapping 
    def pick_boss_to_replace(self, bossparentlist):
        enabled_parents = [b for b in bossparentlist if self.enemy_records[b]["enabled"]]
        bossparent = self.enemy_records[random.choice(enabled_parents)]
        enabled_children = [b for b in bossparent["children"] if self.enemy_records[b]["enabled"]]
        bosschild = self.enemy_records[random.choice(enabled_children)]
        enabled_variations = [b for b in bosschild["variations"] if self.enemy_records[b]["enabled"]]
        return random.choice(enabled_variations)
    def get_enemy_attribute(self, name, attribute):
        pass
    def pick_enemy_to_replace(self, oldenemy, enabledenemies):
        options = [e["name"] for e in enabledenemies if e["category"] == oldenemy["category"]]
        return random.choice(options)
    def perform_randomization(self, options, seed=None):
        print("Enemy Seed: {}".format(seed))
        if diagnostics:
            start_time = time.time()
            print("Starting Randomization: {}".format(options))
        self.unlimited_memory = options["memory_expansion"] if "memory_expansion" in options else False
        scale_enemy = False
        scale_boss = False
        selected_boss = False
        selected_enemy = False
        enemies = None
        bosses = None
        duplicate_enemies = None
        duplicate_bosses = None
        bossmode = None
        enemymode = None
        if "enemy" in options and options["enemy"] != "Disabled":
            enemymode = options["enemy"]
        #duplicate_enemies = enemymode in ["spawnpoint_one_to_one", "wild"]
            enemies = self.get_enemies()
        #     if "scale_enemy_stats" in options:
        #         scale_enemy = options["scale_enemy_stats"]
        #     if "bosses_can_replace_enemies" in options and options["bosses_can_replace_enemies"]:
        #         # Might eventually want to limit this to 10% of replacements get a boss, see how it plays
        #         duplicate_enemies = True
        #         bossenemies = self.filter_enemies(self.get_bosses(), "can_be_enemy")
        #         bossenemies = self.filter_enemies(bossenemies, isfalse=True)
        #         bossenemies = self.add_tag(bossenemies, "large")
        #         enemies = enemies + bossenemies
            if "nightmare_enemies" in options and options["nightmare_enemies"]:
        #         duplicate_enemies = True
                enemies = [e for e in enemies if e["isnightmare"]]
        #     if not ("separate_small_big_enemies" in options and options["separate_small_big_enemies"]):
        #         enemies = self.remove_tag(enemies, "large")
        #     if "selected_enemy" in options and options["selected_enemy"]:
        #         enemymode = "wild"
        #         duplicate_enemies = True
        #         selected_enemy = options["selected_enemy"]
        # TODO BIG ISSUE HERE WITH THE INDENTATION
        if ("boss" in options and options["boss"] != "Disabled"):
            bossmode = options["boss"]
            duplicate_bosses = options["boss"] == "Wild"
            nightmare_bosses = False
            if "nightmare_bosses" in options and options["nightmare_bosses"]:
                nightmare_bosses = True
                duplicate_bosses = True

        if bossmode or enemymode:
            #maxsize = UNLIMITED_SIZE if self.unlimited_memory else LIMITED_SIZE
            maxsize = LIMITED_SIZE
            if bossmode:
                bosses = self.get_bosses(nightmare_mode=nightmare_bosses, maxsize=maxsize)
                if "scale_boss_stats" in options:
                    scale_boss = options["scale_boss_stats"]

                if "selected_boss" in options and options["selected_boss"] and options["boss"] == "Selected Boss":
                    bossmode = "Wild"
                    duplicate_bosses = True
                    selected_boss = options["selected_boss"]
            if enemymode:
                if "selected_enemy" in options and options["selected_enemy"] and options["enemy"] == "Selected Enemy":
                    enemymode = "Wild"
                    duplicate_enemies = True
                    selected_enemy = options["selected_enemy"]
            
            # Probably need a better way to make the category
            category = 'limited'
            # if self.unlimited_memory:
            #     category = 'un' + category
            bossmapping = None
            enemymapping = None
            if bossmode:
                bossmapping = self.pickbossmapping(bosses, category) if not duplicate_bosses else None
            if enemies:
                enemymapping = self.pickenemymapping(enemies)
            
            newspawns = {}
            subtract_map = {}
            spawn_limiters = {}
            msn_mapping = {}
            set_scaling = {}
            object_map = {}
            ai_mods = {}
            self.set_spawns()
            for w in self.spawns:
                world = self.spawns[w]
                for r in world:
                    room = world[r]
                    if "pc" in room and self.unlimited_memory:
                        for k in room["pc"]:
                            room[k] = room["pc"][k]
                    if "ignored" in room and room["ignored"]:
                        # print("Ignoring: ", r)
                        continue
                    if enemies and enemymode == "One to One Per Room":
                        enemymapping = self.pickenemymapping(enemies)
                    for sp in room["spawnpoints"]:
                        changesmade=False
                        spawnpoint = room["spawnpoints"][sp]
                        if "pc" in spawnpoint and self.unlimited_memory:
                            for k in spawnpoint["pc"]:
                                spawnpoint[k] = spawnpoint["pc"][k]
                        if "ignored" in spawnpoint and spawnpoint["ignored"]:
                            # print("Ignoring: ", sp)
                            continue
                        for i in spawnpoint["sp_ids"]:
                            entities = spawnpoint["sp_ids"][i]
                            for e in range(len(entities)):
                                ent = entities[e]

                                def _add_spawn(spawnsies, ent):
                                    if w not in spawnsies:
                                        spawnsies[w] = {}
                                    if r not in spawnsies[w]:
                                        spawnsies[w][r] = {"spawnpoints": {}}
                                    if sp not in spawnsies[w][r]["spawnpoints"]:
                                        spawnsies[w][r]["spawnpoints"][sp] = {"sp_ids": {}}
                                    if i not in spawnsies[w][r]["spawnpoints"][sp]["sp_ids"]:
                                        spawnsies[w][r]["spawnpoints"][sp]["sp_ids"][i] = []
                                    spawnsies[w][r]["spawnpoints"][sp]["sp_ids"][i].append(ent)
                                    return

                                def _add_to_subtract_map(submap, objid):
                                    if w not in submap:
                                        submap[w] = {}
                                    if r not in submap[w]:
                                        submap[w][r] = {"spawnpoints": {}}
                                    if sp not in submap[w][r]["spawnpoints"]:
                                        submap[w][r]["spawnpoints"][sp] = []
                                    submap[w][r]["spawnpoints"][sp].append(objid)

                                def _get_new_ent(old_ent, new_object):
                                    if old_ent == "new":
                                        ent = dict(new_object)
                                        ent["index"] = "new"
                                        return ent
                                    ent = dict(old_ent)
                                    ent["name"] = new_object["name"]
                                    return ent

                                if ent["isboss"]:
                                    if not bosses:
                                        continue # Bosses aren't being randomized
                                    old_boss_object = self.enemy_records[ent["name"]]
                                    old_boss_parent = self.enemy_records[old_boss_object["parent"]]
                                    if old_boss_object["name"] in ["Final Xemnas (Clone)", "Final Xemnas (Clone) (Data)"]:
                                        continue # He gets removed later by subtracts, so don't replace
                                    if not old_boss_object["source_replace_allowed"] and old_boss_object["name"] != "Seifer (2)":
                                        continue
                                    # TODO SEIFER Can't be replaced here normally because it wants an enemy, so just put shadow roxas here
                                    if  old_boss_object["name"] == "Seifer (2)":
                                        new_boss = "Shadow Roxas"
                                    elif selected_boss:
                                        new_boss = selected_boss
                                    elif bossmapping:
                                        if ent["name"] not in bossmapping:
                                            # Boss is not being randomized
                                            continue
                                        new_boss = bossmapping[ent["name"]]
                                    else:
                                        new_boss = self.pick_boss_to_replace(old_boss_parent["available"])
                                    if new_boss == ent["name"]:
                                        continue
                                    new_boss_object = self.enemy_records[new_boss]
                                    if new_boss_object["replace_as"] and not selected_boss:
                                        new_boss_object = self.enemy_records[new_boss_object["replace_as"]]
                                    changesmade = True
                                    _add_spawn(newspawns, _get_new_ent(ent, new_boss_object))
                                    if new_boss == "Shadow Roxas":
                                        continue
                                    for obj in new_boss_object["adds"]:
                                        _add_spawn(newspawns, _get_new_ent("new", obj))
                                    for obj in old_boss_object["subtracts"]+old_boss_object["adds"]:
                                        if "dontSub" in obj and obj["dontSub"]:
                                            continue
                                        _add_to_subtract_map(subtract_map, obj)
                                    if old_boss_object["msn_replace_allowed"] and new_boss_object["msn_replace_allowed"]:
                                        # This is fine because the only bosses with msn_list don't need the msn to be swapped
                                        if not old_boss_object["msn"]:
                                            if old_boss_object["msn_list"]:
                                                continue
                                        if not new_boss_object["msn"]:
                                            if new_boss_object["msn_list"]:
                                                continue
                                        # TEMP FIX THIS WONT ALWAYS WORK PROPER THING TO DO IS DUPLICATE MSNS TO MAKE _RE WORK TODO
                                        msn_mapping[old_boss_object["msn"].replace("_RE", "")] = new_boss_object["msn"].replace("_RE", "")
                                    elif old_boss_object["msn_source_as"]:
                                        msn_mapping[old_boss_object["msn"].replace("_RE", "")] = old_boss_object["msn_source_as"].replace("_RE", "")
                                    if scale_boss:
                                        if new_boss not in set_scaling:
                                            set_scaling[new_boss_object["name"]] = old_boss_object["name"] # So just the first instance of the boss will be used, which isn't great in every scenario TODO
                                    if new_boss_object["obj_edits"]:
                                        object_map[new_boss_object["obj_id"]] = new_boss_object["obj_edits"]
                                    if "aimod" in new_boss_object and new_boss_object["aimod"]:
                                        # In some cases it might be useful to know who is being replaced,
                                        ## IE the height Axel spawns the fire floor might be different on a per room basis
                                        ai_mods[new_boss] = ent["name"]
                                else:
                                    if not enemies:
                                        continue
                                    old_enemy_object = self.enemy_records[ent["name"]]
                                    if not old_enemy_object["source_replace_allowed"]:
                                        continue
                                    if selected_enemy:
                                        new_enemy = selected_enemy
                                    elif enemymapping:
                                        if ent["name"] not in enemymapping:
                                            continue
                                            # if it's not in mapping it's not enabled
                                        new_enemy = enemymapping[ent["name"]]
                                    elif enemymode == "Wild":
                                        new_enemy = self.pick_enemy_to_replace(old_enemy_object, enemies)
                                    if new_enemy == ent["name"]:
                                        continue
                                    changesmade = True
                                    new_enemy_object = self.enemy_records[new_enemy]
                                    if new_enemy_object["replace_as"] and not selected_enemy:
                                        new_enemy_object = self.enemy_records[new_enemy_object["replace_as"]]
                                    _add_spawn(newspawns, _get_new_ent(ent, new_enemy_object))
                                #     elif enemymapping:
                                #         new_enemy = enemymapping[ent["name"]]
                                #     else:
                                #         #Remember tags
                                #         new_enemy = self.pick_enemy_to_replace(ent["name"], enemies)
                                #     oldlimiter = self.getEnemyAttribute(ent["name"], "limiter")
                                #     if new_enemy not in spawn_limiters:
                                #         spawn_limiters[new_enemy] = oldlimiter
                                #     else:
                                #         spawn_limiters[new_enemy] = min(oldlimiter, spawn_limiters[new_enemy])
                                #     if scale_enemy:
                                #         if new_enemy not in set_scaling:
                                #             set_scaling[new_enemy] = []
                                #         set_scaling[new_enemy].append(ent["name"])
                        if changesmade:
                            if "msn_replacement" in spawnpoint and spawnpoint["msn_replacement"]:
                                oldmsn = spawnpoint["msn_replacement"]["original"]
                                newmsn = spawnpoint["msn_replacement"]["new"]
                                msn_mapping[oldmsn] = newmsn
            if diagnostics:
                end_time = time.time()
                print("Randomization Complete: {}s".format(end_time-start_time))
            rand =  {"spawns": newspawns, "msn_map": msn_mapping, "ai_mods": list(set(ai_mods)), "object_map": object_map, "scale_map": set_scaling, "limiter_map": spawn_limiters, "subtract_map": subtract_map}
            if seed:
                rand["seed"] = seed
            return rand
        raise Exception("Didn't randomize anything!")

    def generate_files(self, outdir='', randomization={}, outzip=[]):
        # Generates files in the zip folder and also returns the list of 
        if diagnostics:
            start_time = time.time()
            print("Starting generation of files")
        if outdir:
            def _writeMethod(outfn, relfn, data):
                if not os.path.isdir(os.path.dirname(outfn)):
                    os.makedirs(os.path.dirname(outfn))
                if type(data) == str:
                    data = bytes(data, "utf-8")
                with open(outfn, "wb") as f:
                    f.write(data)
        elif outzip:
            def _writeMethod(outfn, relfn, data):
                outzip.writestr(relfn, data)
        else:
            raise Exception("one of outzip or outdir must be defined")
        assets = []
        if randomization.get("object_map", ""):
            object_map = randomization.get("object_map", "")
            new_object_map = {}
            with open(os.path.join(os.path.dirname(__file__), "data", "objVanilla.yml")) as f:
                obj_data = yaml.load(f)
            for oid in object_map:
                for k in object_map[oid]:
                    obj_data[oid][k] = object_map[oid][k]
                new_object_map[oid] = obj_data[oid]
            asset = self.writeObj(new_object_map, outdir, _writeMethod)
            assets.append(asset)
        if randomization.get("scale_map", ""):
            scale_map = randomization.get("scale_map", "")
            with open(os.path.join(os.path.dirname(__file__), "data", "enmpVanilla.yml")) as f:
                enmp_data_vanilla = yaml.load(f)
                enmp_data_mod = yaml.load(yaml.dump(enmp_data_vanilla))
            for new_enemy in scale_map:
                original_enemy = scale_map[new_enemy]
                new_enmp_index = self.enemy_records[new_enemy]["enmp_index"]
                original_enmp_index = self.enemy_records[original_enemy]["enmp_index"]
                if not new_enmp_index:
                    print("WARNING: Can't scale {}, no ENMP index found".format(new_enemy))
                    continue
                if not original_enmp_index:
                    print("WARNING: Can't scale {}, no ENMP index found".format(original_enemy))
                    continue
                original_enmp_data = enmp_data_vanilla[original_enmp_index]
                new_enmp_data = enmp_data_mod[new_enmp_index]
                new_enmp_data["health"] = original_enmp_data["health"]
                new_enmp_data["level"] = 0 # All bosses are level 0 to take the worlds battle level EXCEPT for datas/terra, which are 99
            asset = self.writeEnmp(enmp_data_mod, outdir, _writeMethod)
            assets.append(asset)
        if randomization.get("spawns", ""):
            self.set_spawns()
            final_fights_spoilers = []
            for w in randomization.get("spawns"):
                world = randomization.get("spawns")[w]
                for room in world:
                    ardname = self.locmap[room]
                    roomasset = {
                        "method": "binarc",
                        "name": "ard/{}.ard".format(ardname),
                        "source": []
                    }
                    basespawns = self.spawns[w][room]
                    roommods = {}
                    if "roommodedits" in basespawns:
                        for rm in basespawns["roommodedits"]:
                            existing_rm = self.getSpawnpoint(ardname, rm)
                            roommodedits[basespawns["roommodedits"][rm]](existing_rm)
                            roommods[rm] = existing_rm
                    for spawnpoint in world[room]["spawnpoints"]:
                        existing = self.getSpawnpoint(ardname, spawnpoint, roommods)
                        for spid in world[room]["spawnpoints"][spawnpoint]["sp_ids"]:
                            sid = int(spid)
                            for ent in world[room]["spawnpoints"][spawnpoint]["sp_ids"][spid]:
                                # Get to the right spawnpointid instance
                                for instance in existing:
                                    if instance["Id"] == sid:
                                        if ent["index"] == "new":
                                            # adding new entity to list, defaulting all values to the first entity in the list
                                            new_ent = dict(instance["Entities"][0])
                                            # Make a unique serial for the spawnpoint?? Maybe 6xx

                                            for attr in ent:
                                                if attr.startswith("mod"):
                                                    baseattr = attr[3:]
                                                    new_ent[baseattr] = new_ent[baseattr] + ent[attr]
                                                elif attr in new_ent:
                                                    new_ent[attr] = ent[attr]


                                            # put the new entity in the existing instance
                                            instance["Entities"].append(new_ent)
                                            

                                            # set the ent index to the proper value
                                            ent["index"] = len(instance["Entities"])-1
                                        elif type(ent["name"]) == int:
                                            for k in ent:
                                                if k == "name":
                                                    instance["Entities"][ent["index"]]["ObjectId"] = ent[k]
                                                elif k == "index":
                                                    pass
                                                else:
                                                    instance["Entities"][ent["index"]][k] = ent[k]
                                        else:
                                            obj = self.lookupObject(ent["name"])

                                            final_txt = final_fight_text(instance["Entities"][ent["index"]], ent["name"])
                                            if final_txt:

                                                final_fights_spoilers.append(final_txt)

                                            oid = obj["obj_id"]
                                            vrs = obj["vars"]

                                            instance["Entities"][ent["index"]]["ObjectId"] = oid
                                            instance["Entities"][ent["index"]]["Argument1"] = vrs[0]
                                            instance["Entities"][ent["index"]]["Argument2"] = vrs[1]
                            if randomization.get("subtract_map", ""):
                                # This is a pretty bad way to do this, tbh
                                try:
                                    entities_to_remove = randomization.get("subtract_map")[w][room]["spawnpoints"][spawnpoint]  
                                except:
                                    # No entities to remove for this spawnpoint
                                    entities_to_remove = None
                                if entities_to_remove:
                                    for instance in existing:
                                        toremove = []
                                        for e in range(len(instance["Entities"])):
                                            ent = instance["Entities"][e]
                                            for etr in entities_to_remove:
                                                if ent["ObjectId"] == etr["ObjectId"]:
                                                    if "Argument1" in etr and etr["Argument1"] != ent["Argument1"]:
                                                        continue
                                                    if "Argument2" in etr and etr["Argument2"] != ent["Argument2"]:
                                                        continue
                                                    toremove.append(e)
                                        for e in sorted(list(set(toremove)))[::-1]:
                                            instance["Entities"].pop(e)
                        spasset = self.writeSpawnpoint(ardname, spawnpoint, existing, outdir, _writeMethod)
                        roomasset["source"].append(spasset)
                        if spawnpoint in roommods:
                            del roommods[spawnpoint]
                    for sp in roommods:
                        spasset = self.writeSpawnpoint(ardname, sp, roommods[sp], outdir, _writeMethod)
                        roomasset["source"].append(spasset)
                    btlfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "btl.script")
                    script = AreaDataScript(open(btlfn).read(), ispc=self.unlimited_memory)
                    for p in script.programs:
                        if script.has_capacity(p):
                            mission = script.get_mission(p)
                            if (not script.ispc) and (not mission):
                                # It's not a big deal if enemies fail to spawn properly in areas where you don't have a mission going on
                                continue 
                            if mission == "\"MU02_MS103B\"":
                                continue # Ambush has some serious issues related to cost
                            script.update_program(p, HARDCAP)
                            programasset = self.writeAreaDataProgram(ardname, "btl", p, script.get_program(p), outdir, _writeMethod)
                            roomasset["source"].append(programasset)
                    assets.append(roomasset)
            if final_fights_spoilers:
                asset = self.writeMSG("eh", final_fights_spoilers, outdir, _writeMethod)
                assets.append(asset)
        if randomization.get("ai_mods", ""):
            for ai in randomization.get("ai_mods"):
                with open(os.path.join(os.path.dirname(__file__), "data", "ai_mods", ai)) as f:
                    edits = f.read().split("\n")
                aifn = edits[0].split("# ")[1].strip()
                edits = [{"offset": int(e.split(" ")[0], 16), "value": e.split(" ")[1]} for e in edits if not e.startswith("#") and len(e) > 0]
                with open(os.path.join(KH2_DIR, "subfiles", "bdx", "obj",  aifn), "rb") as f:
                    data = bytearray(f.read())
                for mod in edits:
                    # They have to be reversed
                    data[mod["offset"]+3] = int(mod["value"][:2], 16)
                    data[mod["offset"]+2] = int(mod["value"][2:4], 16)
                    data[mod["offset"]+1] = int(mod["value"][4:6], 16)
                    data[mod["offset"]] = int(mod["value"][6:8], 16)
                relfn = os.path.join("files", "ai", aifn)
                outfn = os.path.join(outdir, relfn)
                enemy = self.enemy_records[ai]
                _writeMethod(outfn, relfn, data)
                asset = {
                    "method": "binarc",
                    "name": "obj/{}.mdlx".format(enemy["model"]),
                    "source": [
                        {
                            "method": "copy",
                            "name": os.path.basename(aifn).split(".")[0],
                            "source": [{"name": relfn}],
                            "type": "Bdx"
                        }
                    ]
                }
                assets.append(asset)
        if randomization.get("msn_map", ""):
            for oldmsn in randomization.get("msn_map"):
                # Load in the entire msn to memory
                newmsn = randomization["msn_map"][oldmsn]
                newmsnfn = os.path.join(KH2_DIR, "KH2", "msn", "jp", newmsn+".bar")
                with open(newmsnfn, "rb") as f:
                    data = bytearray(f.read())
                # edit the bonus byte
                data[0x0D+self.msninfo[newmsn]["list_offset"]] = self.msninfo[oldmsn]["bonus"]
                # write the msn to the temp folder
                relfn = os.path.join("files", "msns", oldmsn)
                outfn = os.path.join(outdir, relfn)
                _writeMethod(outfn, relfn, data)
                # create the asset
                asset = {
                    "method": "copy",
                    "name": "msn/jp/{}.bar".format(oldmsn),
                    "source": [{"name": relfn}]
                }
                assets.append(asset)
        if diagnostics:
            end_time = time.time()
            print("Files Generated: {}s".format(end_time-start_time))
        return assets

    def writeAreaDataProgram(self, ardname, scripttype, programnumber, program, outdir, writeMethod):
        filename = scripttype+"_"+str(programnumber)+".areadataprogram"
        outfn = os.path.join(outdir, "files", "ard", ardname, filename)
        fn = os.path.join("files", "ard", ardname, filename)
        writeMethod(outfn, fn, program)
        return {
            "method": "areadatascript",
            "name": scripttype,
            "source": [{"name": fn}],
            "type": "AreaDataScript"
        }

    def getSpawnpoint(self, ardname, spawnpoint, altspawns={}):
        if spawnpoint in altspawns.keys():
            return altspawns[spawnpoint]
        with open(os.path.join(KH2_DIR, "subfiles", "spawn", "ard", ardname, "{}.spawn".format(spawnpoint))) as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def writeSpawnpoint(self, ardname, spawnpoint, obj, outdir, writeMethod):
        outfn = os.path.join(outdir, "files", "ard", ardname, spawnpoint+".yml")
        fn = os.path.join("files", "ard", ardname, spawnpoint+".yml")
        writeMethod(outfn, fn, yaml.dump(obj))
        return {
            "method": "spawnpoint",
            "name": spawnpoint,
            "source": [{"name": fn}],
            "type": "AreaDataSpawn"
        }

    def writeEnmp(self, enmp, outdir, writeMethod):
        outfn = os.path.join(outdir, "files", "root", "enmp.list")
        fn = os.path.join("files", "root", "enmp.list")
        data = self.dumpEnmpData(enmp)
        writeMethod(outfn, fn, data)
        return {
            "name": "00battle.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "enmp",
                    "type": "List",
                    "method": "copy",
                    "source": [
                        {
                            "name": fn
                        }
                    ]
                }
            ]
        }

    def writeObj(self, obj, outdir, writeMethod):
        outfn = os.path.join(outdir, "files", "root", "00objentry.bin")
        fn = os.path.join("files", "root", "00objentry.bin")
        writeMethod(outfn, fn, yaml.dump(obj))
        return {
            "name": "00objentry.bin",
            "method": "listpatch",
            "source": [
                {
                    "name": fn,
                    "type": "objentry"
                }
            ]
        }

    def dumpEnmpData(self, enmplist):
        # Every enmp entry is u16
        entrylen = 2
        entries = [
            "id",
            "level",
            "health",
            "maxDamage",
            "minDamage",
            "physicalWeakness",
            "fireWeakness",
            "iceWeakness",
            "thunderWeakness",
            "darkWeakness",
            "lightWeakness",
            "generalWeakness",
            "experience",
            "prize",
            "bonusLevel"
        ]
        def _toBytes(n):
            return n.to_bytes(2, "little")
        header = [2, 0, 0, 0, 229, 0, 0, 0] #taken from vanilla file
        enmp_bytes = bytearray(header)
        for enemy in enmplist:
            for k in entries:
                if k == "health":
                    for healthentry in enemy[k]:
                        enmp_bytes += _toBytes(healthentry)
                    continue
                enmp_bytes += _toBytes(enemy[k])
        return bytes(enmp_bytes)

    def writeMSG(self, name, obj, outdir, writeMethod):
        outfn = os.path.join(outdir, "files", "msg", name+".yml")
        fn = os.path.join("files", "msg", name+".yml")
        writeMethod(outfn, fn, yaml.dump(obj))
        # Whole binarc at once is maybe weird to return
        return {
            "name": "msg/jp/{}.bar".format(name),
            "method": "binarc",
            "source": [
                {
                    "name": name,
                    "type": "list",
                    "method": "kh2msg",
                    "source": [
                        {
                            "name": fn,
                            "language": "en"
                        }
                    ]
                }
            ]
        }

    def lookupObject(self, name):
        return self.enemy_records[name]

    def generate_mod_basics(self, newname=None):
        return {"title": "KH2 Boss/Enemy Rando" if not newname else newname}

class Randomizer:
    def __init__(self, tempdir=None, tempfn=None, deletetmp=True):
        self.tempdir = tempdir or "C:\\temp"
        self.tempfn = tempfn
        self.deletetmp=deletetmp

    def _get_game(self, game):
        if game == "kh2":
            return KingdomHearts2()

    def _validate_options(self, schema, options):
        if type(options) not in [dict, str]:
            raise Exception("Invalid type for options: {}".format(type(options)))
        elif type(options) == str:
            options = json.loads(options)
        for key in options:
            if key not in schema:
                raise Exception("Option {} is not a valid option".format(key))
            else:
                if options[key] not in schema[key]["possible_values"] + schema[key]["hidden_values"]:
                    raise Exception("Option {}-{} is not found in valid options: {}".format(key, options[key], schema[key]))
    
    def _make_tmpdir(self):
        if self.tempfn:
            fn = os.path.join(self.tempdir, self.tempfn)
        else:
            fn = os.path.join(self.tempdir, ''.join(list(str(random.randint(0,10)) for _ in range(7))))
        if os.path.exists(fn):
            print(fn)
            # Realistically this should never happen
            raise Exception("TMP dir already exists, try again")
        os.mkdir(fn)
        rmdir = lambda : shutil.rmtree(fn)
        return fn, rmdir

    def _create_yaml(self, fn, obj):
        with open(fn, "w") as f:
            yaml.dump(obj, f)
    
    def _create_zip(self, moddir, fn):
        # Creates a zip with too many paths
        with ZipFile(fn, "w") as z:
            for folder, _, fns in os.walk(moddir):
                for wfn in fns:
                    pth = os.path.join(folder, wfn)
                    z.write(pth, pth)
        with open(fn, "rb") as f:
            b64zip = base64.encodebytes(f.read())
        os.remove(fn)
        return b64zip

    def generate_filename(self, game, seed, options):
        if type(game) == str:
            game = self._get_game(game)
        name = game.name + "_" + game.schemaversion + "_" + seed + "_"
        validoptions = game.get_options()
        sortedkeys = sorted(validoptions.keys())
        translated = []
        for o in range(len(sortedkeys)):
            key = sortedkeys[o]
            if key in options:
                translated.append(str(o))
                translated.append( str(validoptions[key]["possible_values"].index(options[key])) )
        name += '-'.join(translated)
        name += ".zip"
        return name

    def expand_filename(self, name):
        noextension = name
        if "." in name:
            noextension = name.split(".")[0]
        parts = noextension.split("_")
        if len(parts) != 4:
            raise Exception("Invalid Filename")
        gm = parts[0]
        if gm not in supported_games:
            raise Exception("Game not supported: {}".format(gm))
        game = self._get_game(gm)
        schema = parts[1]
        if schema != game.schemaversion:
            raise Exception("Invalid schema version {}: current version {}".format(schema, game.schemaversion))
        
        compressedoptions = parts[3].split("-")
        options = {}

        validoptions = game.get_options()
        sortedkeys = sorted(validoptions.keys())
        for i in range(0, len(compressedoptions), 2):
            key = sortedkeys[int(compressedoptions[i])]
            value = validoptions[key]["possible_values"][int(compressedoptions[i+1])]
            options[key] = value

        seed = parts[2]
        return gm, seed, options

    def _generate_images(self, fn, outdir):
        import pydenticon
        generator = pydenticon.Generator(10, 10)
        raw_image = generator.generate(fn, 128, 128, output_format="png")
        # image_stream = BytesIO(raw_image)
        with open(os.path.join(outdir, "icon.png"), "wb") as f:
            f.write(raw_image)
        
    def generate_mod(self, game, fn, randomization, newname=None, dumpspoilers=True):
        mod_yaml = game.generate_mod_basics(newname)
        moddir, rmmoddir = self._make_tmpdir()
        
        assets = game.generate_files(moddir, randomization)
        if dumpspoilers:
            with open(os.path.join(moddir, "spoilers.json"), "w") as f:
                json.dump(randomization, f, indent=4)
        mod_yaml["assets"] = assets
        self._create_yaml(os.path.join(moddir, "mod.yml"), mod_yaml)
        
        if GENERATE_IDENTICON:
            self._generate_images(fn, moddir)

        zipped = self._create_zip(moddir, fn)

        if self.deletetmp:
            rmmoddir()

        return zipped

    def read_seed(self, g, seedfn=False, seed=False, outfn="fn"):
        if g not in supported_games:
            raise Exception("Game not supported")
        if not (seedfn or seed):
            raise Exception("Need one of seedfn or seed")
        game = self._get_game(g)
        if seed:
            randomization = seed
        else:
            with open(seedfn) as f:
                if seedfn.endswith("json"):
                    randomization = json.load(f)
                elif seedfn.endswith("yaml"):
                    randomization = yaml.load(f)
                else:
                    raise Exception("Unsupported Seed Format! Need json or yaml")
        return self.generate_mod(game, outfn, randomization, newname=os.path.basename(outfn))

    # My zipped functionality is broken, as the mod randomizer wants just the files in the root of the zip
    def generate_seed(self, g, options, seed=None, randomization_only=False):
        if g not in supported_games:
            raise Exception("Game not supported")
        game = self._get_game(g)
        self._validate_options(game.get_options(), options)
        if not seed:
            seed = str(random.randint(0,100000))
        fn = self.generate_filename(game, seed, options)
        if not seed:
            self.seed = int(time.time())

        randomization = self.generate_randomization(game, options, seed)
        if randomization_only:
            return randomization

        zipped = self.read_seed(g, seed=randomization, outfn=fn)
        return zipped

    def generate_randomization(self, game, options, seed):
        # for both enemies and bosses
        # replacements are either decided beforehand, or at the time of replacement
        random.seed(seed)
        randomization = game.perform_randomization(options, seed=seed)
        
        return randomization

    def generateToZip(self, g, options, modobj, outZip):
        if g not in supported_games:
            raise Exception("Game not supported")
        game = self._get_game(g)
        self._validate_options(game.get_options(), options)
        print(random.randint(0,1000000))

        randomization = game.perform_randomization(options)
        assets = game.generate_files(randomization=randomization, outzip=outZip)
        modobj["assets"] += assets
        return randomization
    
    def getSchemaForGame(self, g):
        if g not in supported_games:
            raise Exception("Game not supported")
        game = self._get_game(g)
        return game.get_options()

if __name__ == '__main__':
    import time
    t = time.time()
    mode = sys.argv[1]
    # run randomizer.py devgenerate "{\"enemy\": \"One to One\"}" randomization_only
    # run randomizer.py devgenerate "{\"boss\": \"Wild\"}"
    # run randomizer.py devgenerate "{\"boss\": \"Selected Boss\", \"selected_boss\": \"Seifer\"}"
    options = sys.argv[2]
    if len(sys.argv) > 3:
        seed = sys.argv[3]
    else:
        seed=None
    if options[0] == "{":
        options = json.loads(options)
    else:
        options = {}
        for arg in sys.argv:
            print(arg)
            if "=" in arg:
                opt = arg.split("=")
                print(opt)
                options[opt[0]] = opt[1]

    if "randomization_only" in sys.argv:
        randomization_only = True
    else:
        randomization_only = False

    if mode.startswith("dev"):
        # moddir = "/mnt/c/Users/15037/git/OpenKh/OpenKh.Tools.ModsManager/bin/debug/net5.0-windows/mods/thundrio-kh"
        #moddir = "C:\\Users\\Arcade\\Desktop\\git\\OpenKh\\OpenKh.Tools.ModsManager\\bin\\Debug\\net5.0-windows\\mods\\thundrio-kh"
        moddir = "C:\\Users\\Arcade\\Desktop\\pcsx2-ex\\openkh\\mods\\thundrio-kh"
        fn = "devmod"
        if os.path.exists(os.path.join(moddir, fn)):
            shutil.rmtree(os.path.join(moddir, fn))
        mode = mode[3:]
    else:
        moddir = "/tmp"
        fn = None

    rando = Randomizer(tempdir=moddir, tempfn=fn, deletetmp=False)
    print("what the fuck")
    if mode == "read":
        print(options)
        b64 = rando.read_seed("kh2", seedfn=options["seed"], outfn=fn)
    else:
        b64 = rando.generate_seed("kh2", options, seed=seed, randomization_only=randomization_only)

    print("Total thing took {}s".format(time.time()-t))