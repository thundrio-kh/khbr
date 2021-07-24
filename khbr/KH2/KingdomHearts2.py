from khbr.textutils import final_fight_text 
from EnemyManager import EnemyManager
from LocationManager import LocationManager
from MissionManager import MissionManager
from SpawnManager import SpawnManager
import os, json

class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "02"
        self.spoilers = {"enemy": {}, "boss": {}}
        self.name = "kh2"
        self.unlimited_memory = False
        self.datalocation = os.path.join(os.path.dirname(__file__), "..", "data", "kh2")
        self.enemy_manager = EnemyManager(self.datalocation)
        self.location_manager = LocationManager(os.path.join(self.datalocation, "location-ard-map.json"))
        self.spawn_manager = SpawnManager()
        self.mission_manager = MissionManager(os.path.join(self.datalocation, "msns.json"))

    def get_valid_enemies(self):
        return self.enemy_manager.get_valid_enemies()
    def get_valid_bosses(self):
        return self.enemy_manager.get_valid_bosses()
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
                                "possible_values": ["Disabled", "One to One", "Wild", "Selected Boss"], "hidden_values": []},
            "selected_boss": {"display_name": "Selected Boss", "description": "Replaces every boss possible with the selected boss. Depending on the boss may not generate a completable seed. This value is ignored if boss mode is not 'Selected Boss'",
                                "possible_values": [None] + sorted(self.get_valid_bosses()), "hidden_values": []},
            "nightmare_bosses": {"display_name": "Nightmare Bosses", "description": "Replaces bosses using only the most difficult bosses in the game. Forces Boss Randomization Mode to be 'Wild'",
                                "possible_values": [False, True], "hidden_values": []},
            "scale_boss_stats": {"display_name": "Scale Bosses", "description": "Attempts force bosses level/HP to the scale of the boss it is replacing. When turned off uses the games scaling which is partially based on the battle level of the world except for Datas/Terra which are always level 99.",
                                "possible_values": [True, False], "hidden_values": []},
            "cups_bosses": {"display_name": "Randomize Cups Bosses", "description": "Include the coliseum bosses in the randomization pool. In 'One for One'.",
                                "possible_values": [True, False], "hidden_values": []},
            "data_bosses": {"display_name": "Randomize Superbosses", "description": "Include the Data versions of organization members in the pool, as well as Terra and Sephiroth",
                                "possible_values": [False, True], "hidden_values": []},
        }
    def get_hidden_options(self):
        # Options that are options but should not show up in the autogenerated UI in the generator
        return {
            # utility mod options
            "remove_damage_cap": {"display_name": "Remove Damage Cap", "description": "Removes the damage cap for all enemies in the game.",
                                "possible_values": [], "hidden_values": [False, True]}
        }

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
    def pickbossmapping(self, bossdict):
        while 1:
            bosslist = [b for b in bossdict if bossdict[b]["name"] == bossdict[b]["parent"]]
            chosen = {}
            for k in sorted(bosslist, key=lambda k: len(bossdict[k]["available"])):
                avail = [b for b in self.enemy_records[k]["available"] if not b in chosen.values()]
                if len(avail) == 0:
                    break
                else:
                    chosen_new_boss = random.choice(avail)
                    chosen[k] = chosen_new_boss
            if len(bosslist) == len(chosen):
                return chosen
    def categorize_enemies(self, enemylist):
        categories = {}
        for e in enemylist:
            parent = self.enemy_records[e["parent"]]
            # Might not be respecting childrens tags properly
            if parent["category"] not in categories:
                categories[parent["category"]] = {}
            categories[parent["category"]][parent["name"]] = parent
        return categories
    def pickenemymapping(self, enemylist, nightmare=None):
        # Create separate lists for each set of tags used by enemies
        categories = self.categorize_enemies(enemylist)
        mapping = {}
        for c in categories:
            og = list(categories[c].values()) # Remove duplicate parent entries
            new = list(og)
            if nightmare:
                new = [e for e in new if e["isnightmare"]]
            random.shuffle(new)
            for i in range(len(og)):
                old_parent = og[i]
                new_parent = new[i % len(new)]
                # So for each child of the new_parent, randomly pick a child of the old_parent
                # Then go through the variations of each, and add them to the mapping
                for old_child_name in old_parent["children"]:
                    new_child_name = random.choice(new_parent["children"])
                    new_child = self.enemy_records[new_child_name]
                    old_child = self.enemy_records[old_child_name]
                    for old_variation_name in old_child["variations"]:
                        new_variation_name = random.choice(list(new_child["variations"]))
                        mapping[old_variation_name] = new_variation_name
                        self.spoilers["enemy"][old_variation_name] = new_variation_name
        assert len(enemylist) == len(list(mapping.keys()))
        
        return mapping 
    def pick_boss_to_replace(self, bossparentlist):
        enabled_parents = [b for b in bossparentlist if self.enemy_records[b]["enabled"]]
        if len(enabled_parents) == 0:
            raise Exception("No available parent bosses!")
        bossparent = self.enemy_records[random.choice(enabled_parents)]
        enabled_children = [b for b in bossparent["children"] if self.enemy_records[b]["enabled"]]
        if len(enabled_children) == 0:
            raise Exception("{} has no enabled children!".format(bossparent["name"]))
        bosschild = self.enemy_records[random.choice(enabled_children)]
        enabled_variations = [b for b in bosschild["variations"] if self.enemy_records[b]["enabled"]]
        if len(enabled_variations) == 0:
            raise Exception("{} has no enabled variations!".format(bosschild["name"]))
        chosen_boss = random.choice(enabled_variations)
        return chosen_boss
    def get_enemy_attribute(self, name, attribute):
        pass
    def pick_enemy_to_replace(self, oldenemy, enabledenemies):
        options = [e["name"] for e in enabledenemies if e["category"] == oldenemy["category"]]
        return random.choice(options)
    def get_boss_list(self, options):
        nightmare_bosses = "nightmare_bosses" in options and options["nightmare_bosses"]
        maxsize = LIMITED_SIZE
        bosses = self.get_bosses(nightmare_mode=nightmare_bosses, maxsize=maxsize)

        # cups and superbosses are turned off by default
        # This feels too imperative to me, I want the randomizer to be as moduler/functional as possible
        exclude_tags = []
        if not ("cups_bosses" in options and options["cups_bosses"]):
            exclude_tags.append("cups")
        if not ("data_bosses" in options and options["data_bosses"]):
            exclude_tags.append("data")

        # Nightmare mode ignores the datas and cups options
        if nightmare_bosses:
            bosses = {b: bosses[b] for b in bosses if bosses[b]["isnightmare"]}
        else:
            bosses = {b: bosses[b] for b in bosses if len(set(bosses[b]["tags"]).intersection(set(exclude_tags))) == 0}

        boss_names = list(bosses.keys())


        # Need to adjust the children and variation and availablelists to not contain bosses which should be excluded
        # this still feels pretty imperative, maybe during a refactor it will become obvious how to be more functional
        # have to look at every source boss too so adjusting those sources, not just the ones that are available
        for boss_name in self.enemy_records:
            boss = self.enemy_records[boss_name]
            if boss["type"] != "boss":
                continue
            if boss["name"] == boss["parent"]:
                boss["children"] = [b for b in boss["children"] if b in bosses]
                boss["available"] = [b for b in boss["available"] if b in bosses]
                for child_name in boss["children"]:
                    child = self.enemy_records[child_name]
                    # This is involved in ommitting children that are excluded via tag
                    child["variations"] = [b for b in child["variations"] if b in bosses]
        return bosses
    def perform_randomization(self, options, seed=None):
        print_debug("Enemy Seed: {}".format(seed), override=False)
        if diagnostics:
            start_time = time.time()
            print_debug("Starting Randomization: {}".format(options), override=True)
        self.unlimited_memory = options["memory_expansion"] if "memory_expansion" in options else False
        scale_enemy = False
        scale_boss = False
        if "scale_boss_stats" in options:
            scale_boss = options["scale_boss_stats"]
        selected_boss = False
        selected_enemy = False
        enemies = None
        bosses = None
        duplicate_enemies = None
        duplicate_bosses = None
        bossmode = None
        nightmare_enemies = False
        enemymode = None
        utility_mods = []
        if options.get("remove_damage_cap"):
            utility_mods.append("remove_damage_cap")
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
                #ewwww imperative
                nightmare_enemies = True
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
                bosses = self.get_boss_list(options)
                if "selected_boss" in options and options["selected_boss"] and options["boss"] == "Selected Boss":
                    bossmode = "Wild"
                    duplicate_bosses = True
                    selected_boss = options["selected_boss"]
                elif nightmare_bosses:
                    bossmode = "Wild"
                    duplicate_bosses = True

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
                bossmapping = self.pickbossmapping(bosses) if not duplicate_bosses else None
            if enemies:
                enemymapping = self.pickenemymapping(enemies, nightmare=nightmare_enemies)
            newspawns = {}
            subtract_map = {}
            spawn_limiters = {}
            msn_mapping = {}
            set_scaling = {}
            object_map = {}
            ai_mods = {}
            data_replacements = {}
            
            self.set_spawns()
            for w in self.spawns:
                world = self.spawns[w]
                for r in world:
                    room = world[r]
                    if "pc" in room and self.unlimited_memory:
                        for k in room["pc"]:
                            room[k] = room["pc"][k]
                    if "ignored" in room and room["ignored"]:
                        # print_debug("Ignoring: ", r)
                        continue
                    if enemies and enemymode == "One to One Per Room":
                        enemymapping = self.pickenemymapping(enemies, nightmare=nightmare_enemies)
                    for sp in room["spawnpoints"]:
                        changesmade=False
                        spawnpoint = room["spawnpoints"][sp]
                        if "pc" in spawnpoint and self.unlimited_memory:
                            for k in spawnpoint["pc"]:
                                spawnpoint[k] = spawnpoint["pc"][k]
                        if "ignored" in spawnpoint and spawnpoint["ignored"]:
                            # print_debug("Ignoring: ", sp)
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
                                    if bossmode == "Wild" and "onetooneonly" in old_boss_object["tags"]:
                                        continue
                                    # TODO SEIFER Can't be replaced here normally because it wants an enemy, so just put shadow roxas here
                                    if  old_boss_object["name"] == "Seifer (2)":
                                        new_boss = "Shadow Roxas"
                                    elif selected_boss:
                                        new_boss = selected_boss
                                    else:
                                        new_boss_parent = None
                                        if bossmapping:
                                            if old_boss_parent["name"] not in bossmapping:
                                                # Boss is not being randomized
                                                continue
                                            new_boss_parent = bossmapping[old_boss_parent["name"]]
                                        if new_boss_parent:
                                            bosspicklist = [new_boss_parent]
                                        elif old_boss_parent["name"] in data_replacements:
                                            bosspicklist = [data_replacements[old_boss_parent["name"]]]
                                        else:
                                            bosspicklist = old_boss_parent["available"]
                                        new_boss = self.pick_boss_to_replace(bosspicklist)
                                        if "roxas" in old_boss_object["tags"]:
                                            if new_boss == "Axel (Data)":
                                                # This fight is probably not very winnable as roxas, so force to normal axel II
                                                new_boss = "Axel II"
                                        if "solo" in old_boss_object["tags"]:
                                            if new_boss == "Demyx (Data)":
                                                new_boss = "Demyx" # Actual fix would be to just mod the ai to increase the time for destroying clones
                                    self.spoilers["boss"][ent["name"]] = new_boss
                                    if new_boss == ent["name"]:
                                        continue
                                    new_boss_object = self.enemy_records[new_boss]
                                    # Due to how they use the same MSN in a lot of cases, org replacements should be the same between nobody + data versions
                                    if "organization" in old_boss_object["tags"]:
                                        new_parent = new_boss_object["parent"]
                                        data_replacements[old_boss_parent["name"]] = new_parent

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
                                        # I don't think the .replace is needed because datas and normal fights are the same
                                        # but in some cases the _RE does need to be replaced like Xaldin
                                        # but for ones where the _RE doesn't exist, it's not doing any harm
                                        # msn_mapping[old_boss_object["msn"].replace("_RE", "")] = new_boss_object["msn"].replace("_RE", "")
                                        msn_mapping[old_boss_object["msn"]] = new_boss_object["msn"]
                                    elif old_boss_object["msn_source_as"]:
                                        #msn_mapping[old_boss_object["msn"].replace("_RE", "")] = old_boss_object["msn_source_as"].replace("_RE", "")
                                        msn_mapping[old_boss_object["msn"]] = old_boss_object["msn_source_as"]
                                    if new_boss not in set_scaling:
                                        if "sourcemaxhp" in old_boss_object["tags"]:
                                            set_scaling[new_boss_object["name"]] = 5000 # I think this will be fine because it's all in stt but could theoretically overload the max hp display which crashes with scan
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
                                    old_name = ent["nameForReplace"] if "nameForReplace" in ent else ent["name"]
                                    old_enemy_object = self.enemy_records[old_name]
                                    if not old_enemy_object["source_replace_allowed"]:
                                        continue
                                    if selected_enemy:
                                        new_enemy = selected_enemy
                                    elif enemymapping:
                                        if old_name not in enemymapping:
                                            continue
                                            # if it's not in mapping it's not enabled
                                        new_enemy = enemymapping[old_name]
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
                print_debug("Enemy Randomization Complete: {}s".format(end_time-start_time))
            # DEBUG
            #print_debug(self.create_spoiler_text(), override=True)
            # 0/0
            rand =  {"utility_mods": utility_mods,"spawns": newspawns, "msn_map": msn_mapping, "ai_mods": list(set(ai_mods)), "object_map": object_map, "scale_map": set_scaling, "limiter_map": spawn_limiters, "subtract_map": subtract_map}
            if seed:
                rand["seed"] = seed
            return rand
        if not utility_mods:
            raise Exception("Didn't randomize anything!")
        return {"utility_mods": utility_mods}

    def generate_files(self, outdir='', randomization={}, outzip=[]):
        # Generates files in the zip folder and also returns the list of 
        if diagnostics:
            start_time = time.time()
            print_debug("Starting generation of files")
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
        utility_mods = randomization.get("utility_mods", [])
        if randomization.get("object_map", ""):
            object_map = randomization.get("object_map", "")
            new_object_map = {}
            with open(os.path.join(os.path.dirname(__file__), "data", "objVanilla.yml")) as f:
                obj_data = yaml.load(f, Loader=yaml.SafeLoader)
            for oid in object_map:
                for k in object_map[oid]:
                    obj_data[oid][k] = object_map[oid][k]
                new_object_map[oid] = obj_data[oid]
            asset = self.writeObj(new_object_map, outdir, _writeMethod)
            assets.append(asset)
        if randomization.get("scale_map", {}) or "remove_damage_cap" in utility_mods:
            scale_map = randomization.get("scale_map", {})
            with open(os.path.join(os.path.dirname(__file__), "data", "enmpVanilla.yml")) as f:
                enmp_data_vanilla = yaml.load(f, Loader=yaml.SafeLoader)
                enmp_data_mod = yaml.load(yaml.dump(enmp_data_vanilla), Loader=yaml.SafeLoader)
            for new_enemy in scale_map:
                original_enemy = scale_map[new_enemy]
                new_enmp_index = self.enemy_records[new_enemy]["enmp_index"] # really its the id not the index anymore
                if not new_enmp_index:
                    print_debug("WARNING: Can't scale {}, no ENMP index found".format(new_enemy))
                    continue
                def _get_index(source, idnum):
                    for i in range(len(source)):
                        if source[i]["id"] == idnum:
                            return i
                    raise Exception("This shouldn't happen")
                new_enmp_data = enmp_data_mod[_get_index(enmp_data_vanilla, new_enmp_index)]

                if type(original_enemy) == int: #ie 2000
                    new_enmp_data["health"][0] = original_enemy
                else:
                    original_enmp_index = self.enemy_records[original_enemy]["enmp_index"]
                
                    if not original_enmp_index:
                        print_debug("WARNING: Can't scale {}, no ENMP index found".format(original_enemy))
                        continue
                    original_enmp_data = enmp_data_vanilla[_get_index(enmp_data_vanilla, original_enmp_index)]
                    new_enmp_data["health"] = original_enmp_data["health"]
                if DEBUG_HEALTH:
                    new_enmp_data["health"] = [DEBUG_HEALTH for _ in original_enmp_data["health"]]
                new_enmp_data["level"] = 0 # All bosses are level 0 to take the worlds battle level EXCEPT for datas/terra, which are 99
            if "remove_damage_cap" in utility_mods:
                for en in enmp_data_mod:
                    en["maxDamage"] = 0xFFFF
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
                    with open(btlfn) as f:
                        script = AreaDataScript(f.read(), ispc=self.unlimited_memory)
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
        #TODO need way for adjusting the final fight MSNs to make retrying retry directly, but the value is a bitflag array, so treat carefully
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
            print_debug("Files Generated: {}s".format(end_time-start_time))
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
            "multi": [
                {"name": "msg/us/{}.bar".format(name)},
                {"name": "msg/uk/{}.bar".format(name)}
            ],
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