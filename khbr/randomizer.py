import time, json, random, os, shutil, yaml, base64, sys
from zipfile import ZipFile
import random


supported_games = ["kh2"]

KH2_DIR = os.environ["USE_KH2_GITPATH"]
RANDOMIZATIONS_DIR = os.path.join(KH2_DIR,"randomizations") if os.path.exists(os.path.join(KH2_DIR,"randomizations")) else "randomizations"

UNLIMITED_SIZE = 99_999_999_999_999
LIMITED_SIZE = 10_000_000
NUM_RANDOMIZATION_MAPPINGS = 9
class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "01"
        self.name = "kh2"
        with open(os.path.join(os.path.dirname(__file__), "location-ard-map.json")) as f:
            self.locmap = json.load(f)
        with open(os.path.join(os.path.dirname(__file__), "msns.json")) as f:
            self.msninfo = json.load(f)
        self.enemy_records = self.get_bosses(usefilters=False, getavail=False)
    def get_valid_enemies(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "enemy"]
    def get_valid_bosses(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "boss"]
    def get_options(self):
        # Might want to define valid predicates at some point, as certain combinations can't be selected together
        return {
            "enemy": {"display_name": "Enemy Randomization Mode", "description": "Select if and how the enemies should be randomized. Available choices: One-to-One replacement ie all shadows become dusks. One-to-One per spawn: One-to-One but every spawnpoint is different (so shadows in Parlor might be ice cubes, but in LOD Cave they might be fire cubes). Wild: every enemy entity in the game is completely randomized",
                                  "possible_values": ["Disabled", "One to One", "One to One Per Spawn", "Wild", "Selected Enemy"]},
            "selected_enemy": {"display_name": "Selected Enemy", "description": "Replaces every enemy with the selected enemy. Depending on the enemy may not generate a completable seed. This value is ignored if enemy randomization mode is not 'Selected Enemy'",
                                "possible_values": self.get_valid_enemies()},
            # "bosses_can_replace_enemies": {"display_name": "Bosses Can Replace Enemies", "description": "Replaces a small percentage of enemies in the game with a random boss. This option is intended for PC use only.",
            #                     "possible_values": [False, True]},
            "nightmare_enemies": {"display_name": "Enemies of Eternal Darkness", "description": "Replaces enemies using only the most difficult enemies in the game.",
                                "possible_values": [False, True]},
            # "separate_small_big_enemies": {"display_name": "Separate Small and Big Enemies", "description": "Randomizes big enemies among themselves and small enemies among themselves. Useful to prevent crashing"},
            #                     "possible_values": [True, False]},
            # "scale_enemy_stats": {"display_name": "Scale Enemy Stats", "description": "Attempts to scale enemies to the level/HP of the enemy it is replacing.",
            #                     "possible_values": [True, False]},

            # "memory_expansion": {"display_name": "Use Expanded Memory", "description": "The PS2 version of the game is limited to 32MB of memory, which constrains where bosses and enemies can be placed. Turn this option on if playing on PC to remove these constraints.",
            #                     "possible_values": [True, False]},

            "boss": {"display_name": "Boss Randomization Mode", "description": "Select if and how the bosses should be randomized. Available choices: One-to-One replacement just shuffles around where the bosses are located, but each boss is still present (some bosses may be excluded from the randomization). Wild will randomly pick an available boss for every location, meaning some bosses can be seen more than once, and some may never be seen. Selected Boss will replace every boss with a single selected boss.",
                                "possible_values": ["Disabled", "One to One", "Selected Boss", "Wild"]},#, "one_to_one_characters",
            "nightmare_bosses": {"display_name": "Bosses of Eternal Darkness", "description": "Replaces bosses using only the most difficult bosses in the game.",
                                "possible_values": [False, True]},
            # "scale_boss_stats": {"display_name": "Scale Bosses", "description": "Attempts to scale bosses to the level/HP of the boss it is replacing.",
            #                     "possible_values": [True, False]},
            "selected_boss": {"display_name": "Selected Boss", "description": "Replaces every boss possible with the selected boss. Depending on the boss may not generate a completable seed. This value is ignored if boss mode is not 'Selected Boss'",
                                "possible_values": self.get_valid_bosses()}
        }
    def get_enemies(self):
        enemies = self.get_valid_enemies()
        return [self.enemy_records[e] for e in self.get_valid_enemies() if self.enemy_records[e]["enabled"]]
    def get_bosses(self, nightmare_mode=False, maxsize=UNLIMITED_SIZE, usefilters=True, getavail=True):
        defaults = {
            "replace_as": None,
            "replace_allowed": True,
            "model": None,
            "msn_replace_allowed": True,
            "tags": [],
            "category": None,
            "level": 0,
            "isnightmare": False,
            "hp": 100,
            "limiter": 1,
            "msn_required": False,
            "aimod": None,
            "can_be_enemy": False,
            "msn": None,
            "size": 0,
            "enmp_index": None,
            "enabled": True,
            "blacklist": [],
            "whitelist": []
        }
        with open(os.path.join(os.path.dirname(__file__), "enemies.json")) as f:
            bosses_f = json.load(f)
        bosses = {}
        allkeys = []
        for bn in bosses_f:
            b = bosses_f[bn]
            for v in b["variations"]:
                boss = dict(b["variations"][v])
                boss["name"] = v
                for k in b:
                    allkeys.append(k)
                    if k == "variations":
                        continue
                    if k not in boss:
                        boss[k] = b[k]
                for d in defaults:
                    if d not in boss:
                        boss[d] = defaults[d]
                boss["category"] = '-'.join(boss["tags"])
                if usefilters:
                    if boss["type"] != 'boss':
                        continue
                    if not boss['enabled']:
                        continue
                    if nightmare_mode and not ("isnightmare" in boss and boss["isnightmare"]):
                        continue
                bosses[v] = boss
        if getavail:
            locations = self.get_locations()

            for w in locations:
                world = locations[w]
                for r in world:
                    room = world[r]
                    for sp in room["spawnpoints"]:
                        spawnpoint = room["spawnpoints"][sp]
                        for spid in spawnpoint["sp_ids"].values():
                            for ent in spid:
                                if ent["isboss"]:
                                    if ent["name"] in bosses:
                                        bosses[ent["name"]]["room_size"] = room["size"]
            for b in bosses:
                boss = bosses[b]
                avail = [] # These are bosses that are allowed to be here
                for bc in bosses:
                    boss_check = bosses[bc]
                    if boss_check["name"] == boss["name"]:
                        # Boss should always be allowed to be in it's own location
                        avail.append(boss_check["name"])
                        continue
                    if "blacklist" in boss:
                        if bc in boss["blacklist"]:
                            continue
                    if boss["whitelist"]:
                        if bc not in boss["whitelist"]:
                            continue
                    else:
                        if boss["msn_required"]:
                            if not boss_check["msn_replace_allowed"]:
                                continue
                        if boss["size"] + boss_check["room_size"] >= maxsize:
                            continue
                    avail.append(boss_check["name"])
                boss["available"] = avail
        return bosses
    def get_locations(self):
        with open(os.path.join(os.path.dirname(__file__), "locations.json")) as f:
            locations_f = json.load(f)
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
        dirname = os.path.join(os.path.dirname(__file__), "randomizations", category)
        num = random.randint(1,num_files)
        with open(os.path.join(dirname, str(num))) as f:
            return json.load(f)
    def pickenemymapping(self, enemylist):
        pass 
    def pick_boss_to_replace(self, bosslist):
        n = random.randint(0,len(bosslist)-1)
        return bosslist[n]
    def get_enemy_attribute(self, name, attribute):
        pass
    def pick_enemy_to_replace(self, oldenemy, enabledenemies):
        options = [e["name"] for e in enabledenemies if e["category"] == oldenemy["category"]]
        return random.choice(options)
    def perform_randomization(self, options):
        unlimited_memory = options["memory_expansion"] if "memory_expansion" in options else False
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
        print(options)
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
            maxsize = UNLIMITED_SIZE if unlimited_memory else LIMITED_SIZE
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
            if unlimited_memory:
                category = 'un' + category
            bossmapping = None
            enemymapping = None
            if bossmode:
                bossmapping = self.pickbossmapping(bosses, category) if not duplicate_bosses else None
            # enemymapping = self.pickenemymapping(enemies) if not duplicate_bosses else None
            spawns = self.get_locations()
            newspawns = {}
            spawn_limiters = {}
            msn_mapping = {}
            set_scaling = {}
            ai_mods = {}
            for w in spawns:
                world = spawns[w]
                for r in world:
                    room = world[r]
                    if "ignored" in room:
                        continue
                    # if enemies and enemymode == "spawnpoint_one_to_one":
                    #     enemymapping = self.pickenemymapping(enemies)
                    for sp in room["spawnpoints"]:
                        spawnpoint = room["spawnpoints"][sp]
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
                                
                                def _get_new_ent(old_ent, new_object):
                                    ent = dict(old_ent)
                                    ent["name"] = new_object["name"]
                                    return ent

                                if ent["isboss"]:
                                    if not bosses:
                                        continue # Bosses aren't being randomized
                                    if selected_boss:
                                        new_boss = selected_boss
                                    elif bossmapping:
                                        if ent["name"] not in bossmapping:
                                            # Boss is not being randomized
                                            continue
                                        new_boss = bossmapping[ent["name"]]
                                    else:
                                        if ent["name"] not in bosses:
                                            continue # Boss can't be randomized (eg jafar)
                                        new_boss = self.pick_boss_to_replace(bosses[ent["name"]]["available"])
                                    if new_boss == ent["name"]:
                                        continue
                                    new_boss_object = self.enemy_records[new_boss]
                                    old_boss_object = self.enemy_records[ent["name"]]
                                    if not old_boss_object["replace_allowed"]:
                                        continue
                                    _add_spawn(newspawns, _get_new_ent(ent, new_boss_object))
                                    # Bosses don't have spawn limiters normally, so don't need to set them
                                    if old_boss_object["msn_replace_allowed"]:
                                        msn_mapping[old_boss_object["msn"]] = new_boss_object["msn"] 
                                    if scale_boss:
                                        if new_boss not in set_scaling:
                                            hp = old_boss_object["hp"]
                                            level = old_boss_object["level"]
                                            set_scaling[new_boss] = (hp, level)
                                        else:
                                            hp = old_boss_object["hp"]
                                            level = old_boss_object["level"]
                                            if hp > set_scaling[new_boss][0]:
                                                set_scaling[new_boss] = (hp, level)
                                    if "aimod" in new_boss_object and new_boss_object["aimod"]:
                                        # In some cases it might be useful to know who is being replaced,
                                        ## IE the height Axel spawns the fire floor might be different on a per room basis
                                        ai_mods[new_boss] = ent["name"]
                                else:
                                    if not enemies:
                                        continue
                                    old_enemy_object = self.enemy_records[ent["name"]]
                                    if not old_enemy_object["replace_allowed"]:
                                        continue
                                    if selected_enemy:
                                        new_enemy = selected_enemy
                                    elif enemymapping:
                                        pass
                                    elif enemymode == "Wild":
                                        new_enemy = self.pick_enemy_to_replace(old_enemy_object, enemies)
                                    if new_enemy == ent["name"]:
                                        continue
                                    
                                    new_enemy_object = self.enemy_records[new_enemy]
                                    
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

            return {"spawns": newspawns, "msn_map": msn_mapping, "ai_mods": list(set(ai_mods)), "scale_map": set_scaling, "limiter_map": spawn_limiters}
        raise Exception("Didn't randomize anything!")

    def generate_files(self, outdir='', randomization={}, outzip=[]):
        # Generates files in the zip folder and also returns the list of 
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
        if randomization.get("spawns", ""):
            for world in randomization.get("spawns").values():
                for room in world:
                    ardname = self.locmap[room]
                    roomasset = {
                        "method": "binarc",
                        "name": "ard/{}.ard".format(ardname),
                        "source": []
                    }
                    for spawnpoint in world[room]["spawnpoints"]:
                        existing = self.getSpawnpoint(ardname, spawnpoint)
                        for spid in world[room]["spawnpoints"][spawnpoint]["sp_ids"]:
                            sid = int(spid)
                            for ent in world[room]["spawnpoints"][spawnpoint]["sp_ids"][spid]:
                                # Get to the right spawnpointid instance
                                for instance in existing:
                                    if instance["Id"] == sid:
                                        if ent["index"] == "new":
                                            # adding new entity to list, defaulting all values to the first entity in the list
                                            new_ent = dict(instance["Entities"][0])
                                            # put the new entity in the existing instance
                                            instance["Entities"].append(new_ent)
                                            # set the ent index to the proper value
                                            ent["index"] = len(instance["Entities"])-1
                                        if type(ent["name"]) == int:
                                            for k in ent:
                                                if k == "name":
                                                    instance["Entities"][ent["index"]]["ObjectId"] = ent[k]
                                                elif k == "index":
                                                    pass
                                                else:
                                                    instance["Entities"][ent["index"]][k] = ent[k]
                                        else:
                                            obj = self.lookupObject(ent["name"])
                                            oid = obj["obj_id"]
                                            vrs = obj["vars"]

                                            instance["Entities"][ent["index"]]["ObjectId"] = oid
                                            instance["Entities"][ent["index"]]["SpawnArgument"] = vrs[0]
                                            instance["Entities"][ent["index"]]["Argument1"] = vrs[1]
                                            instance["Entities"][ent["index"]]["Argument2"] = vrs[2]
                        spasset = self.writeSpawnpoint(ardname, spawnpoint, existing, outdir, _writeMethod)
                        roomasset["source"].append(spasset)
                    assets.append(roomasset)
        if randomization.get("ai_mods", ""):
            for ai in randomization.get("ai_mods"):
                with open(os.path.join(os.path.dirname(__file__), "data", "ai_mods", ai)) as f:
                    edits = f.read().split("\n")
                aifn = edits[0].split("# ")[1].strip()
                edits = [{"offset": int(e.split(" ")[0], 16), "value": e.split(" ")[1]} for e in edits if not e.startswith("#") and len(e) > 0]
                with open(os.path.join(KH2_DIR, "subfiles", "bdx", "obj",  aifn), "rb") as f:
                    data = bytearray(f.read())
                for mod in edits:
                    data[mod["offset"]] = int(mod["value"][:2], 16)
                    data[mod["offset"]+1] = int(mod["value"][2:4], 16)
                    data[mod["offset"]+2] = int(mod["value"][4:6], 16)
                    data[mod["offset"]+3] = int(mod["value"][6:8], 16)
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
                            "name": aifn.split(".")[0],
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
        return assets

    def getSpawnpoint(self, ardname, spawnpoint):
        with open(os.path.join(KH2_DIR, "subfiles", "spawn", "ard", ardname, "{}.spawn".format(spawnpoint))) as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def writeSpawnpoint(self, ardname, spawnpoint, obj, outdir, writeMethod):
        outfn = os.path.join(outdir, "files", ardname, spawnpoint+".yml")
        fn = os.path.join("files", ardname, spawnpoint+".yml")
        writeMethod(outfn, fn, yaml.dump(obj))
        return {
            "method": "spawnpoint",
            "name": spawnpoint,
            "source": [{"name": fn}],
            "type": "AreaDataSpawn"
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
                if options[key] not in schema[key]["possible_values"]:
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
        
    def generate_mod(self, game, fn, randomization, newname=None):
        mod_yaml = game.generate_mod_basics(newname)
        moddir, rmmoddir = self._make_tmpdir()
        
        # For icon generate an identicon based on the filename+game
        assets = game.generate_files(moddir, randomization)
        mod_yaml["assets"] = assets
        self._create_yaml(os.path.join(moddir, "mod.yml"), mod_yaml)
        
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
                randomization = json.load(f)
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
        randomization = game.perform_randomization(options)
        
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
    mode = sys.argv[1]
    # {"selected_boss": "Past Pete", "boss": "selected_boss"}
    options = sys.argv[2]
    if len(sys.argv) > 3:
        seed = sys.argv[3]
    else:
        seed=None
    if options[0] == "{":
        options = json.loads(options)

    if mode.startswith("dev"):
        moddir = "/mnt/c/Users/15037/git/OpenKh/OpenKh.Tools.ModsManager/bin/debug/net5.0-windows/mods/thundrio-kh"
        fn = "devmod"
        if os.path.exists(os.path.join(moddir, fn)):
            shutil.rmtree(os.path.join(moddir, fn))
        mode = mode[3:]
    else:
        moddir = "/tmp"
        fn = None

    rando = Randomizer(tempdir=moddir, tempfn=fn, deletetmp=False)
    
    if mode == "read":
        b64 = rando.read_seed("kh2", seedfn=options, outfn=fn)
    else:
        b64 = rando.generate_seed("kh2", options, seed=seed)