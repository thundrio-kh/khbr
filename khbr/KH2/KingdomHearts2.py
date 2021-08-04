from khbr.textutils import final_fight_text 
from khbr.utils import print_debug
from khbr._config import diagnostics
from khbr.randutils import pickbossmapping, pickenemymapping, pick_boss_to_replace, pick_enemy_to_replace
from EnemyManager import EnemyManager
from LocationManager import LocationManager
from MissionManager import MissionManager
from SpawnManager import SpawnManager
from schemas.random_config import RandomConfig
import os, time

#TODO data should be under kh2
class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "02"
        self.spoilers = {"enemy": {}, "boss": {}}
        self.name = "kh2"
        self.unlimited_memory = False
        self.datalocation = os.path.join(os.path.dirname(__file__), "..", "data", "kh2")
        self.enemy_manager = EnemyManager(self.datalocation)
        self.location_manager = LocationManager(self.datalocation)
        self.spawn_manager = SpawnManager()
        self.mission_manager = MissionManager(self.datalocation)

    def get_valid_enemies(self):
        return self.enemy_manager.get_valid_enemies()
    def get_valid_bosses(self):
        return self.enemy_manager.get_valid_bosses()
        
    @staticmethod
    def get_utility_mods(options):
        utility_mods = []
        if options.get("remove_damage_cap"):
            utility_mods.append("remove_damage_cap")
        return utility_mods

    def perform_randomization(self, options, seed=None):
        print_debug("Enemy Seed: {}".format(seed), override=False)
        if diagnostics:
            start_time = time.time()
            print_debug("Starting Randomization: {}".format(options), override=True)

        enemymode = options.get("enemy", 'Disabled')
        bossmode = options.get("boss", "Disabled")
        nightmare_bosses = options.get("nightmare_bosses")
        config = RandomConfig(
            unlimited_memory = options.get("memory_expansion"),
            utility_mods = self.get_utility_mods(options),
            scale_boss = options.get("scale_boss_stats"),

            enemymode = enemymode,
            enemies = self.get_enemies() if enemymode != 'Disabled' else {},
            nightmare_enemies = options.get("nightmare_enemies"),

            bossmode = bossmode,
            nightmare_bosses = nightmare_bosses,
            duplicate_bosses = nightmare_bosses or bossmode in ["Wild", "Selected Boss"],
            bosses = self.get_boss_list(options) if bossmode != 'Disabled' else {}
        )
        if enemymode == "Selected Enemy":
            config.enemies = [options["selected_enemy"]]
        if bossmode == "Selected Boss":
            config.bosses = [options["selected_boss"]]

        rand_seed = {}
        if bossmode or enemymode:
            rand_seed = self.create_seed(config)

        if config.utility_mods:
            rand_seed["utility_mods"] = config.utility_mods
        if not rand_seed:
            raise Exception("Didn't randomize anything!")

    def create_seed(self, config: RandomConfig):
            bossmapping = pickbossmapping(self.enemy_manager.enemy_records, config.bosses) if not config.duplicate_bosses else None
            if config.enemies and config.enemymode != "Selected Enemy":
                categorized_enemies = self.enemy_manager.categorize_enemies(config.enemies)
                enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemies"], nightmare=config.nightmare_enemies)
            
            
            newspawns = {}
            subtract_map = {}
            spawn_limiters = {}
            msn_mapping = {}
            set_scaling = {}
            object_map = {}
            ai_mods = {}
            data_replacements = {}
            
            spawns = self.location_manager.get_locations()
            for w, world in spawns.items():
                for r, room in world.items():
                    self.location_manager.update_room(room, config.unlimited_memory)
                    if room.get("ignored"):
                        continue
                    if config.enemymode == "One to One Per Room":
                        enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemies"], nightmare=config.nightmare_enemies)
                    for sp, spawnpoint in room["spawnpoints"].items():
                        changesmade=False
                        self.location_manager.update_location(spawnpoint, config.unlimited_memory)
                        if spawnpoint.get("ignored"):
                            continue
                        for i, entities in spawnpoint["sp_ids"].items():
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
                                    if r not in submap[w]:c8pawnpoints"]:
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