from khbr.textutils import final_fight_text
from khbr.KH2.Mission import Mission
from khbr.KH2.AiManager import AiManager
from khbr.utils import print_debug
from khbr._config import KH2_DIR, HARDCAP, DEBUG_HEALTH
from khbr.KH2.AreaDataScript import AreaDataScript
import os, yaml


# TODO future refactor could use jsonpath to make looking through the complex spawns dict easier
class AssetGenerator:
    def __init__(self, modwriter, spawn_manager = None, location_manager=None, enemy_manager = None, ispc=False):
        self.assets = []
        self.modwriter = modwriter
        self.enemy_manager = enemy_manager
        self.location_manager = location_manager
        self.spawn_manager = spawn_manager
        self.ispc = ispc

    def generateObjEntry(self, object_map):
        if not object_map:
            return
        new_object_map = {}
        with open(os.path.join(os.path.dirname(__file__), "data", "objVanilla.yml")) as f:
            obj_data = yaml.load(f, Loader=yaml.SafeLoader)
        for oid in object_map:
            for k in object_map[oid]:
                obj_data[oid][k] = object_map[oid][k]
            new_object_map[oid] = obj_data[oid]
        asset = self.modwriter.writeObj(new_object_map)
        self.assets.append(asset)

    def generateEnmp(self, scale_map, remove_damage_cap):
        if not (scale_map or remove_damage_cap):
            return

        with open(os.path.join(os.path.dirname(__file__), "data", "enmpVanilla.yml")) as f:
            enmp_data_vanilla = yaml.load(f, Loader=yaml.SafeLoader)
            enmp_data_modified = yaml.load(yaml.dump(enmp_data_vanilla), Loader=yaml.SafeLoader)
        #TODO I don't really know whats happening inside this for loop
        for new_enemy in scale_map:
            original_enemy = scale_map[new_enemy]

            new_enmp_index = self.enemy_manager.enemy_records[new_enemy]["enmp_index"] # really its the id not the index anymore
            if not new_enmp_index:
                print_debug("WARNING: Can't scale {}, no ENMP index found".format(new_enemy))
                continue
            def _get_index(source, idnum):
                for i in range(len(source)):
                    if source[i]["id"] == idnum:
                        return i
                raise Exception("This shouldn't happen")
            new_enmp_data = enmp_data_modified[_get_index(enmp_data_vanilla, new_enmp_index)]

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
        if remove_damage_cap:
            for en in enmp_data_modified:
                en["maxDamage"] = 0xFFFF
        asset = self.writeEnmp(enmp_data_modified)
        self.assets.append(asset)

    def generateAiMods(self, ai_mods):
        if not ai_mods:
            return
        for ai in ai_mods:
            with open(os.path.join(os.path.dirname(__file__), "data", "ai_mods", ai)) as f:
                edits_string = f.read().split("\n")
            ai_manager = AiManager(edits_string)

            with open(os.path.join(KH2_DIR, "subfiles", "bdx", "obj",  ai_manager.aifn), "rb") as f:
                data = bytearray(f.read())

            ai_manager.modify_data(data)
            
            self.modwriter.writeAi

            enemy = self.enemy_manager.enemy_records[ai]
            modelname = enemy["model"]

            asset = self.modwriter.writeAi(self.ai_manager.fn, modelname, data)
            self.assets.append(asset)

    def generateMsns(self, msn_map, msninfo):
        #TODO need way for adjusting the final fight MSNs to make retrying retry directly, but the value is a bitflag array, so treat carefully
        for oldmsn in msn_map:
            # Load in the entire msn to memory
            new_msn_name = msn_map.get(oldmsn)
            info = msninfo[info]
            mission = Mission(new_msn_name, info)
            
            bonus_byte = self.msninfo[oldmsn]["bonus"]
            mission.edit_bonus_byte(bonus_byte)
            
            asset = self.modwriter.writeMsn(oldmsn, mission.data)

            self.assets.append(asset)

    def generateSpawns(self, original_spawns, replacement_spawns, subtract_map):
        if not replacement_spawns:
            return

        text_spoilers = {
            "final_fights": []
        }

        for w, world in replacement_spawns.items():
            for r, room in world.items():
                ardname = self.location_manager.locmap[r]
                roomasset = {
                    "method": "binarc",
                    "name": "ard/{}.ard".format(ardname),
                    "source": []
                }

                basespawns = original_spawns[w][r]
                roommods = self.spawn_manager.apply_room_mods(basespawns, ardname)

                for spn, spawnpoint in room["spawnpoints"].items():
                    existing_spawnpoint = self.spawn_manager.getSpawnpoint(ardname, spn, roommods)
                    for i, spid in spawnpoint["sp_ids"].items():
                        for new_entity in spid:
                            old_spid = self.spawn_manager.getSpId(existing_spawnpoint, int(spid))
                            # Get to the right spawnpointid sp_instance
                            old_spawn = new_entity["index"]

                            if new_entity["index"] == "new":
                                self.spawn_manager.add_new_object(old_spid, new_entity)
                            elif type(new_entity["name"]) == int:
                                self.spawn_manager.set_object_by_id(old_spid["Entities"][old_spawn], new_entity)
                            else:
                                obj = self.enemy_manager.lookupObject(new_entity["name"])

                                final_txt = final_fight_text(old_spawn, new_entity["name"])
                                if final_txt:
                                    text_spoilers["final_fights"].append(final_txt)

                                self.spawn_manager.set_object_by_rec(old_spid, obj)

                        if subtract_map:
                            entities_to_remove = subtract_map.get(w, {}).get(r, {}).get("spawnpoints", {}).get(spn, []) 
                            if entities_to_remove:
                                self.spawn_manager.subtract_spawns()
                        
                    spasset = self.modwriter.writeSpawnpoint(ardname, spawnpoint, existing_spawnpoint)
                    roomasset["source"].append(spasset)
                    if spawnpoint in roommods:
                        del roommods[spawnpoint]
                for sp in roommods:
                    spasset = self.modwriter.writeSpawnpoint(ardname, sp, roommods[sp])
                    roomasset["source"].append(spasset)

                self.update_area_data_programs(ardname, roomasset["source"])
            
                self.assets.append(roomasset)
        if text_spoilers["final_fights"]:
            textasset = self.modwriter.writeMSG("eh", text_spoilers["final_fights"])
            self.assets.append(textasset)

    def update_area_data_programs(self, ardname, roomsource):
        btlfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "btl.script")
        with open(btlfn) as f:
            script = AreaDataScript(f.read(), ispc=self.ispc)
        for p in script.programs:
            if script.has_capacity(p):
                mission = script.get_mission(p)
                if (not script.ispc) and (not mission):
                    # It's not a big deal if enemies fail to spawn properly in areas where you don't have a mission going on
                    continue 
                if mission == "\"MU02_MS103B\"":
                    continue # Ambush has some serious issues related to cost
                script.update_program(p, HARDCAP)
                programasset = self.modwriter.writeAreaDataProgram(ardname, "btl", p, script.get_program(p))
                roomsource.append(programasset)