from khbr.KH2.schemas.enemyseed import EnemySeed
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

        rand_seed = EnemySeed(config=config)
        if bossmode or enemymode:
            self.create_seed(rand_seed)

        if config.utility_mods:
            rand_seed.utility_mods = config.utility_mods

        rand_seed_json= rand_seed.toJson()
        if not rand_seed_json:
            raise Exception("Didn't randomize anything!")

        if seed:
            rand_seed_json["seed"] = seed

        if diagnostics:
            end_time = time.time()
            print_debug("Enemy Randomization Complete: {}s".format(end_time-start_time))

        return rand_seed_json

    def create_seed(self, config: RandomConfig, rand_seed: EnemySeed):
            rand_seed.bossmapping = pickbossmapping(self.enemy_manager.enemy_records, config.bosses) if not config.duplicate_bosses else None
            if config.enemies and config.enemymode != "Selected Enemy":
                categorized_enemies = self.enemy_manager.categorize_enemies(config.enemies)
                rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemies"], nightmare=config.nightmare_enemies)
            
            spawns = self.location_manager.get_locations()
            for w, world in spawns.items():
                for r, room in world.items():
                    self.location_manager.update_location(room, config)
                    if room.get("ignored"):
                        continue
                    if config.enemymode == "One to One Per Room":
                        rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemies"], nightmare=config.nightmare_enemies)
                    
                    for sp, spawnpoint in room["spawnpoints"].items():
                        self.location_manager.update_location(spawnpoint, config)
                        if spawnpoint.get("ignored"):
                            continue
                        for i, entities in spawnpoint["sp_ids"].items():
                            # TODO might be able to make this just for entity in entities
                            for e in range(len(entities)):
                                entity = entities[e]

                                if config.bosses and entity["isboss"]:
                                    old_boss_object = self.enemy_manager.enemy_records[entity["name"]]
                                    old_boss_parent = self.enemy_manager.get_parent(entity["name"])
                                    if not self.spawn_manager.should_replace_boss(old_boss_object, config, rand_seed):
                                        continue

                                    new_boss = self.spawn_manager.get_new_boss(old_boss_object, old_boss_parent, config, rand_seed)        
                                    if not new_boss:
                                        continue
                                    self.spoilers["boss"][entity["name"]] = new_boss
                                    # same replacement
                                    if not new_boss or new_boss == old_boss_object["name"]:
                                        continue

                                    new_boss_object = self.enemy_manager.get_new_boss_object(old_boss_object, new_boss, rand_seed)

                                    self.rand_seed.add_spawn(w, r, sp, i, entity, new_boss_object)
                                    #TODO spoilers should move into rand_seed
                                    self.rand_seed.update_seed(old_boss_object, new_boss_object)

                                elif config.enemies and not entity["isboss"]:
                                    old_enemy_object = self.get_enemy_object_from_entity(entity)

                                    if not self.spawn_manager.should_replace_enemy(old_enemy_object):
                                        continue

                                    new_enemy = self.spawn_manager.get_new_enemy(rand_seed, old_enemy_object)
                                    if not new_enemy or new_enemy == old_enemy_object["name"]:
                                        continue

                                    new_enemy_object = self.enemy_manager.get_new_enemy_object(new_enemy, rand_seed)
                                    self.rand_seed.add_spawn(w, r, sp, i, entity, new_enemy_object)
        
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