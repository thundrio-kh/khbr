import math
from khbr.KH2.CommandManager import CommandManager
from khbr.KH2.MemtManager import MemtManager
from khbr.textutils import final_fight_text
from khbr.KH2.Mission import Mission
from khbr.KH2.AiManager import AiManager
from khbr.KH2.LuaManager import LuaManager
from khbr._config import KH2_DIR, HARDCAP, DEBUG_HEALTH
from khbr.KH2.AreaDataScript import AreaDataScript
from khbr.randutils import log_output
import os, yaml
import random


# TODO future refactor could use jsonpath to make looking through the complex spawns dict easier
class AssetGenerator:
    def __init__(self, modwriter, spawn_manager = None, location_manager=None, enemy_manager = None, ispc=False, is_boss_rush=False, force_story_boss_levels=False):
        self.assets = []
        self.modwriter = modwriter
        self.enemy_manager = enemy_manager
        self.location_manager = location_manager
        self.spawn_manager = spawn_manager
        self.ispc = ispc
        self.is_boss_rush=is_boss_rush
        self.force_story_boss_levels=force_story_boss_levels

    #TODO this might be super slow
    def find_asset(self, assetname, default=None):
        for asset in self.assets:
            if asset["name"].endswith(assetname):
                return asset
        if not default:
            return None
        self.assets.append(default)
        return default

    def generatePlrp(self, hp=20, mp=100, ap=50, accessoryslt=3, armorslt=3, itemslt=3, items=[]):
        # Must give to noncrit and crit version of sora
        def _genobj(character, charid):
            itms = [int(i) for i in items]
            while len(itms) < 32:
                itms.append(0)
            return {
            "AccessorySlotMax": accessoryslt,
            "Ap": ap,
            "ArmorSlotMax": armorslt,
            "Character": character,
            "Hp": hp,
            "Mp": mp,
            "Id": charid,
            "ItemSlotMax": itemslt,
            "Items": itms,
            "Padding": [0 for _ in range(52)]
        }
        plrp = [_genobj(1, 0)]
        asset = self.modwriter.writePlrp(plrp)
        existingasset = self.find_asset("00battle.bin")
        if existingasset:
            existingasset["source"].append(asset["source"][0])
        else:
            self.assets.append(asset)

    
    def generateObjEntry(self, object_map, apply_better_stt=False):
        if not (object_map or apply_better_stt):
            return
        new_object_map = {}
        with open(os.path.join(os.path.dirname(__file__), "data", "objVanilla.yml")) as f:#
            obj_data = yaml.load(f, Loader=yaml.SafeLoader)
        stt_data = None
        if apply_better_stt:
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "better_stt", "ObjList_Better_STT.yml")) as f:
                stt_data = yaml.load(f, Loader=yaml.SafeLoader)
            # smell because objVanilla has a Flag attribute, whereas ObjList_Better_STT has all of the Flag attributes as their own keys. Might not matter for what we are doing but if issues crop up look here
            for key in stt_data:
                obj_data[key] = stt_data[key]
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
                log_output("WARNING: Can't scale {}, no ENMP index found".format(new_enemy), log_level=1)
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
                original_enmp_index = self.enemy_manager.enemy_records[original_enemy]["enmp_index"]
            
                if not original_enmp_index:
                    log_output("WARNING: Can't scale {}, no ENMP index found".format(original_enemy), log_level=0)
                    continue
                original_enmp_data = enmp_data_vanilla[_get_index(enmp_data_vanilla, original_enmp_index)]
                new_enmp_data["health"] = original_enmp_data["health"]
            if DEBUG_HEALTH:
                new_enmp_data["health"] = [DEBUG_HEALTH for _ in original_enmp_data["health"]]
                log_output(new_enemy)
            # Health value should be capped at Terras due to HP visibility issue
            new_enmp_data["health"][0] = min(new_enmp_data["health"][0], 1878)
            new_enmp_data["level"] = 0 # All bosses are level 0 to take the worlds battle level EXCEPT for datas/terra, which are 99
        if remove_damage_cap:
            for en in enmp_data_modified:
                en["maxDamage"] = 0xFFFF
        for enemy in enmp_data_modified:
            if enemy["id"] == 141:
                enemy["health"][0] = 500 # MCP health needs to be halved
        asset = self.modwriter.writeEnmp(enmp_data_modified)
        self.assets.append(asset)

    def generateCustomMovesets(self, apply_form_movement=False, apply_better_stt=False):        
        # sora moveset
        with open(os.path.join(os.path.dirname(__file__), "data", "bin", "B_EX100.mset"), "rb") as f:
            mset_data = f.read()
        asset = self.modwriter.writeMset("B_EX100.mset", mset_data)
        self.assets.append(asset)
        if apply_form_movement:
            # valor
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "shananas_form_movement", "P_EX100_BTLF.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("P_EX100_BTLF.mset", mset_data)
                self.assets.append(asset)
            # anti
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "shananas_form_movement", "P_EX100_HTLF.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("P_EX100_HTLF.mset", mset_data)
                self.assets.append(asset)
            # limit
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "shananas_form_movement", "P_EX100_KH1F.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("P_EX100_KH1F.mset", mset_data)
                self.assets.append(asset)
            # wisdom
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "shananas_form_movement", "P_EX100_MAGF.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("P_EX100_MAGF.mset", mset_data)
                self.assets.append(asset)
            # master
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "shananas_form_movement", "P_EX100_TRIF.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("P_EX100_TRIF.mset", mset_data)
                self.assets.append(asset)
            # final
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "shananas_form_movement", "P_EX100_ULTF.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("P_EX100_ULTF.mset", mset_data)
                self.assets.append(asset)
        if apply_better_stt:
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "better_stt", "B_EX100_SR.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("B_EX100_SR.mset", mset_data)
                self.assets.append(asset)
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "better_stt", "F_TT010.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("F_TT010.mset", mset_data)
                self.assets.append(asset)
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "better_stt", "P_EX110.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("P_EX110.mset", mset_data)
                self.assets.append(asset)
            with open(os.path.join(os.path.dirname(__file__), "data", "bin", "better_stt", "W_EX010_RX.mset"), "rb") as f:
                mset_data = f.read()
                asset = self.modwriter.writeMset("W_EX010_RX.mset", mset_data)
                self.assets.append(asset)
            
    def generateBetterSTT(self):
        with open(os.path.join(os.path.dirname(__file__), "data", "bin", "better_stt", "trinity_zz.bar"), "rb") as f:
            trinity_data = f.read()
            asset = self.modwriter.writeBin(trinity_data, "trinity_zz.bar", os.path.join("limit", "fm", "trinity_zz.bar")) # this might not work on pc
            self.assets.append(asset)

    def generateCustomCmd(self, cmd_mods):
        vanilla_cmd = yaml.load(open(os.path.join(os.path.dirname(__file__), "data", "cmdVanilla.yml"), "r"), Loader=yaml.SafeLoader)
        def _get_entry(index):
            for i in vanilla_cmd:
                if i["Id"] == index:
                    return i
        cmd_to_apply = []
        for index, changes in cmd_mods.items():
            vanilla_cmd_entry = dict(vanilla_cmd[index]) #_get_entry(index)
            for change in changes:
                vanilla_cmd_entry[change] = changes[change]
            cmd_to_apply.append(vanilla_cmd_entry)
        asset = self.modwriter.writeCmd(cmd_to_apply)
        self.assets.append(asset)

    def generateCustomMemt(self, randomize_party, randomize_costumes):
        memt = MemtManager(os.path.join(os.path.dirname(__file__), "data", "bin", "memt.bin"))

        if randomize_costumes:
            # Costume rando
            
            wtypes = ["v", "wi", "nm", "xm", "tr"]
            replacements = {}
            sora_shuffled = list(wtypes)
            random.shuffle(sora_shuffled)
            sora_replacements = {wtypes[i]:sora_shuffled[i] for i in range(len(wtypes))}
            donald_shuffled = list(wtypes)
            random.shuffle(donald_shuffled)
            donald_replacements = {wtypes[i]:donald_shuffled[i] for i in range(len(wtypes))}
            goofy_shuffled = list(wtypes)
            random.shuffle(goofy_shuffled)
            goofy_replacements = {wtypes[i]:goofy_shuffled[i] for i in range(len(wtypes))}

            for entry in memt.entries:
                for k in memt.sora_keys:
                    old_value = entry[k]
                    if old_value in memt.costume_map:
                        category = memt.costume_map[old_value]
                        new_category = sora_replacements[category]
                        new_value = memt.costumes["sora"][k][new_category]
                        entry[k] = new_value
                old_value = entry["Friend 1 (Donald)"]
                if old_value in memt.costume_map:
                    category = memt.costume_map[old_value]
                    new_category = donald_replacements[category]
                    new_value = memt.costumes["Friend 1 (Donald)"][new_category]
                    entry["Friend 1 (Donald)"] = new_value
                old_value = entry["Friend 2 (Goofy)"]
                if old_value in memt.costume_map:
                    category = memt.costume_map[old_value]
                    new_category = goofy_replacements[category]
                    new_value = memt.costumes["Friend 2 (Goofy)"][new_category]
                    entry["Friend 2 (Goofy)"] = new_value

        if randomize_party:
            # Party member rando

            party_member_map = {}
            for k,v in memt.party_members.items():
                for obj_id in v:
                    party_member_map[obj_id] = k
            original = list(memt.party_members.keys())
            shuffled = list(memt.party_members.keys())
            random.shuffle(shuffled)
            replacements = {}
            for i in range(len(original)):
                replacements[original[i]] = shuffled[i]
            for entry in memt.entries:
                # donald_value = entry["Friend 1 (Donald)"]
                # if donald_value in party_members["donald"]: # that means we are allowed to change the value
                #     entry["Friend 1 (Donald)"] = random.choice(party_members[replacements["donald"]])
                # goofy_value = entry["Friend 2 (Goofy)"]
                # if goofy_value in party_members["goofy"]: # that means we are allowed to change the value
                #     entry["Friend 1 (Goofy)"] = random.choice(party_members[replacements["goofy"]])
                worldvalue = entry["World Character"]
                if worldvalue:
                    if worldvalue == 2257: # Riku final battle -> normal riku
                        worldvalue = 2073
                    worldfriend = party_member_map[worldvalue]
                entry["World Character"] = random.choice(memt.party_members[replacements[worldfriend]])
            #log_output(replacements) # DEBUG ONLY KEEP COMMENTED
        asset = self.modwriter.writeMemt(memt.dump_bin())
        existingasset = self.find_asset("03system.bin")
        if existingasset:
            existingasset["source"].append(asset["source"][0])
        else:
            self.assets.append(asset)

    def generateAiMods(self, ai_mods, rvlrando=None):
        created_mods = {}
        for name,mods in ai_mods.items():
            log_output(str(name)+","+str(mods) )
            for mod in mods:
                modelname = name.split("/")[0]
                modbasename = os.path.basename(name)
                modfilename = os.path.join(os.path.dirname(__file__), "data", "bdscript", mod["type"], name)
                if os.path.isdir(modfilename):
                    possible_fns = os.listdir(modfilename)
                    modfilename = os.path.join(modfilename, possible_fns[0].replace(".original",""))
                    modbasename = os.path.basename(modfilename).split(".")[0]
                if not modelname in created_mods:
                    with open(modfilename) as f:
                        ai_manager = AiManager(modelname, f.read())
                else:
                    ai_manager = created_mods[modelname]["manager"]            

                if mod.get("vars", {}).get("modification") == "drop_dataspace_orbs":
                    ai_manager.drop_dataspace_orbs()
                else:
                    for orig,new in mod.get("replacements", {}).items():
                        ai_manager.replace(orig, mod["vars"][new])

                created_mods[modelname] = {
                    "name": modbasename,
                    "model": modelname,
                    "type": mod["type"],
                    "manager": ai_manager
                }

        if rvlrando:
            rando_type = rvlrando.replace("revenge_limit_rando", "")
            # TODO there are extra karma values left in the list at the end, so I'm clearly not finding everything I should 
            karma_values = [92.0, 75.0, 92.0, 75.0, 100.0, 75.0, 75.0, 55.0, 75.0, 75.0, 75.0, 75.0, 100.0, 100.0, 75.0, 75.0, 75.0, 50.0, 80.0, 75.0, 100.0, 75.0, 100.0, 75.0, 100.0, 5.0, 200.0, 200.0, 200.0, 200.0, 50.0, 80.0, 60.0, 60.0, 60.0, 60.0, 50.0, 40.0, 40.0, 75.0, 100.0, 75.0, 100.0, 150.0, 125.0, 50.0, 50.0, 30.0, 60.0, 60.0, 100.0, 100.0, 100.0, 100.0, 80.0, 70.0, 60.0, 50.0, 100.0, 80.0, 60.0, 40.0, 100.0, 80.0, 60.0, 40.0, 100.0, 80.0, 60.0, 40.0, 100.0, 80.0, 60.0, 40.0, 50.0, 95.0, 90.0, 85.0, 80.0, 100.0, 40.0]

            if rando_type == "Vanilla":
                pass # pass
            elif rando_type == "Set 0":
                karma_values = [0 for _ in karma_values]
            elif rando_type == "Set Infinity":
                karma_values = [9999 for _ in karma_values]
            elif rando_type == "Random Swap":
                random.shuffle(karma_values)
            elif rando_type == "Random Values":
                karma_values = [random.randint(0,200) for _ in karma_values]
            else:
                raise Exception("Invalid Karma Limit Value: {}".format(rando_type))

            objdir = os.path.join(os.path.dirname(__file__), "data", "bdscript", "obj")
            for modelname in os.listdir(objdir):
                # ignoring these things that are not enemies (ie sora book or thresholders heartless)
                if modelname in ["B_BB130", "B_CA000", "B_EX380", "B_EX390", "B_EX410"]:
                    continue
                aifiles = [f for f in os.listdir(os.path.join(objdir, modelname)) if "original" not in f]
                if len(aifiles) != 1:
                    raise Exception("Wrong number of files for {}: {}".format(modelname, len(aifiles)))
                if modelname in created_mods:
                    created_mods[modelname]["manager"].set_karma_limit(karma_values)
                else:
                    modfilename = os.path.join(objdir, modelname, aifiles[0]).replace(".bdscript", ".original.bdscript")
                    with open(modfilename) as f:
                        ai_manager = AiManager(modfilename, f.read())

                        ai_manager.set_karma_limit(karma_values)

                        created_mods[modelname] = {
                            "name": aifiles[0],
                            "model": modelname,
                            "type": "obj",
                            "manager": ai_manager
                        }

        for modelname, ai in created_mods.items():
            asset = self.modwriter.writeAi(ai["name"], ai["model"], ai["type"], ai["manager"].get_script())
            self.assets.append(asset)

    def generateLuaMods(self, lua_mods):
        if not lua_mods:
            return
        for lua_name in lua_mods:
            lua = LuaManager(lua_name)
            lua.create_file()

            asset = self.modwriter.writeLua(lua.fn, lua.data)
            self.assets.append(asset)

    def generateMsns(self, msn_map, msninfo):
        for oldmsn in msn_map:

            new_msn_mapping = msn_map.get(oldmsn)
            if type(new_msn_mapping) == str:
                new_msn_mapping = {"name": new_msn_mapping}
            new_msn_name = new_msn_mapping["name"]

            # This might cause some issues with bosses like the FF bosses because the camera complete won't work, and of course it prevents mickey in some fights, which is most likely fine
            if self.find_asset(oldmsn+".bar"):
                log_output("Old MSN {} has an ai edit, so can't copy over {}".format(oldmsn, new_msn_name), log_level=1)
                continue
            info = msninfo[new_msn_name]
            mission = Mission(new_msn_name, info)

            bonus_byte = new_msn_mapping.get("setbonus", msninfo[oldmsn]["bonus"])
            mission.set_bonus_byte(bonus_byte)

            if "disablecamera" in new_msn_mapping:
                mission.set_camera_complete_byte()
            if "setmickey" in new_msn_mapping:
                mission.set_mickey_bit(new_msn_mapping["setmickey"])
            if "setxp" in new_msn_mapping:
                mission.set_noxp_bit(not new_msn_mapping["setxp"])
            if "setretry" in new_msn_mapping:
                mission.set_retry_bit(new_msn_mapping["setretry"])
            
            asset = self.modwriter.writeMsn(oldmsn, mission.data)

            self.assets.append(asset)

    def getDefaultRoomAsset(self, ardname):
        # Ideally this would be 
        formattedname =  "ard/{}.ard".format(ardname)
        roomasset = {
            "method": "binarc",
            "name": formattedname,
            "source": []
        }
        # if region:
        multi = [{"name": formattedname.replace("ard/", r)} for r in ["ard/us/", "ard/jp/","ard/fr/","ard/gr/","ard/it/","ard/sp/","ard/uk/"]]
        roomasset["multi"] = multi
        return roomasset

    def generateSpawns(self, replacement_spawns, subtract_map):
        original_spawns = self.location_manager.locations

        if not replacement_spawns:
            return

        text_spoilers = {
            "final_fights": []
        }

        def getworld(b):
            if b.get("msn"):
                return b["msn"][:2]
            # msn list is HE
            return "HE"
        def getroom(b):
            if b.get("msn"):
                r = b["msn"][2:4]
                if r.lower() != "_c":
                    return r
            return "09" # Assume colosseum

        for w, world in replacement_spawns.items():
            for r, room in world.items():
                ardname = self.location_manager.get_ardname(r)
                
                roomasset = self.getDefaultRoomAsset(ardname)

                basespawns = original_spawns[w][r]
                btlmods = {"adds": basespawns.get("battlescriptadds", {}) }
                if self.is_boss_rush:
                    for k,v in basespawns.get("battlescriptadds_br", {}).items():
                        btlmods["adds"][k] = v
                evtmods = {"fix_settings": []}

                roommods = self.spawn_manager.apply_room_mods(basespawns, ardname)
                
                for spn, spawnpoint in room["spawnpoints"].items():
                    existing_spawnpoint = self.spawn_manager.getSpawnpoint(ardname, spn, roommods)
                    #default_object = dict(existing_spawnpoint[0]["Entities"][0])

                    def _update_spid(i, spid, custom_unit_list):
                        gr2_self_replace = False
                        for new_entity in spid:
                            old_spid = self.spawn_manager.getSpId(existing_spawnpoint, int(i))
                            # Get to the right spawnpointid sp_instance
                            old_spawn_index = new_entity["index"]

                            if new_entity.get("customUnit", False):
                                cu = new_entity["customUnit"]
                                cu_id = cu["Id"]
                                if not cu_id in custom_unit_list:
                                    custom_unit_list[cu_id] = self.spawn_manager.getNewUnit(cu)
                                del new_entity["customUnit"]
                                self.spawn_manager.add_new_object(custom_unit_list[cu_id], new_entity)#, default_object=default_object)
                            elif new_entity["index"] == "new":
                                self.spawn_manager.add_new_object(old_spid, new_entity)
                            elif type(new_entity["name"]) == int:
                                self.spawn_manager.set_object_by_id(old_spid["Entities"][old_spawn_index], new_entity)
                            else:

                                obj = self.enemy_manager.lookup_object(new_entity["name"])

                                if old_spawn_index >= len(old_spid["Entities"]):
                                    continue # Case like AX1 room where AX1 was replaced subtracting the spawns that got replaced by the icy cube... Smelly way to fix this
                                old_spawn = old_spid["Entities"][old_spawn_index]
                                old_obj = self.enemy_manager.lookup_object_by_id(old_spawn["ObjectId"])
                                if old_obj.get("story_level", 0) > 0 and self.force_story_boss_levels:
                                    prg = old_obj["program"]
                                    if old_obj["program"] in btlmods["adds"]:
                                        btlmods["adds"][prg].append("BattleLevel {}".format(old_obj["story_level"]))
                                    else:
                                        btlmods["adds"][prg] = ["BattleLevel {}".format(old_obj["story_level"])]
                                if "fix_source_area_settings" in old_obj["tags"] and self.is_boss_rush:
                                    evtmods["fix_settings"].append({"world": getworld(old_obj), "room": getroom(old_obj), "program": old_obj["program"], "options": {"fix_source_area_settings": True} })

                                if old_spawn["ObjectId"] == 1543 and new_entity["name"] == "Grim Reaper II" and old_spawn["Argument1"] == 0: # Grim Reaper II is replacing itself
                                    gr2_self_replace = True

                                final_txt = final_fight_text(old_spawn, new_entity["name"])
                                if final_txt:
                                    text_spoilers["final_fights"].append(final_txt)

                                self.spawn_manager.set_object_by_rec(old_spawn, obj)

                        if subtract_map:
                            entities_to_remove = subtract_map.get(w, {}).get(r, {}).get("spawnpoints", {}).get(spn, []) 
                            if gr2_self_replace:
                                entities_to_remove = []
                            if entities_to_remove:
                                self.spawn_manager.subtract_spawns(existing_spawnpoint, entities_to_remove)
                        
                        if gr2_self_replace:
                            for entity in existing_spawnpoint[0]["Entities"]:
                                entity["Medal"] = 0

                    custom_unit_list = {} # keyed on ID
                    for i, spid in spawnpoint["sp_ids"].items():
                        _update_spid(i, spid, custom_unit_list)
                    for cid, unit in custom_unit_list.items():
                        if cid in [s["Id"] for s in existing_spawnpoint]:
                            log_output("Warning: spid already exists in spawnpoint, test for problems. {} {}".format(cid, ardname), log_level=1) # DEBUG ONLY
                        existing_spawnpoint.append(unit)
                    
                    spasset = self.modwriter.writeSpawnpoint(ardname, spn, existing_spawnpoint)
                    roomasset["source"].append(spasset)
                    if spn in roommods:
                        del roommods[spn]
                for sp in roommods:
                    spasset = self.modwriter.writeSpawnpoint(ardname, sp, roommods[sp])
                    roomasset["source"].append(spasset)

                # Generalize if you need more files like this
                # For now it's only needed for OC Cups
                if ardname == "he09":
                    basename = "he09.btl.ps2.areadatascript"
                    if self.ispc:
                        basename = basename.replace("ps2","pc")
                    assetpath = os.path.join(os.path.dirname(__file__), "data", basename)
                    programasset = self.modwriter.writeCopiedSubfile(ardname, "btl", "AreaDataScript", assetpath)
                    roomasset["source"].append(programasset)
                else:
                    self.update_area_data_programs(ardname, roomasset["source"], btlmods)

                for evt_mod in evtmods["fix_settings"]:
                    self.generateEvt(evt_mod["world"], evt_mod["room"], evt_mod["program"], roomasset["source"], options=evt_mod["options"])
            
                self.assets.append(roomasset)
        if text_spoilers["final_fights"]:
            textasset = self.modwriter.writeMSG("eh", text_spoilers["final_fights"])
            self.assets.append(textasset)

    def update_area_data_programs(self, ardname, roomsource, btlmods={}):
        def _can_update_capacity(ispc, prg):
            if not prg.has_command("Capacity"):
                return False
            if ardname in ["mu07", "mu09"]:
                # Summit will crash when capacity is infinite, and shan yu's summons can sometimes crash the game
                return False
            mission = prg.get_mission()
            if (not ispc) and (not mission):
                # It's not a big deal if enemies fail to spawn properly in areas where you don't have a mission going on
                return False             
            if mission == "MU02_MS103B":
                return False # Ambush has some serious issues related to cost
            return True

        #btlmods = {} 
        btlfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "btl.script")
        with open(btlfn) as f:
            script = AreaDataScript(f.read(), ispc=self.ispc)
        for p in script.programs:
            prg = script.programs[p]
            if _can_update_capacity(script.ispc, prg):
                prg.update_capacity(HARDCAP)
            if self.ispc:
                if prg.has_command("Spawn"):
                    prg.add_packet_spec()
                    prg.add_enemy_spec()
            if p in btlmods.get("adds",{}):
                for l in btlmods["adds"][p]:
                    prg.add_line(l)
            programasset = self.modwriter.writeAreaDataProgram(ardname, "btl", p, prg.make_program())
            roomsource.append(programasset)

    def generateEvt(self, world, room, programnumber, roomsource, options=None):
        def _ser(j):
            sp = j.split()
            return {
                "Type": sp[1],
                "World": sp[3],
                "Area": sp[5],
                "Entrance": sp[7],
                "LocalSet": sp[9],
                "FadeType": sp[11]
            }

        log_output("DEBUG: making {} {} evt program {}, {}".format(world,room,programnumber,options))
        if not options:
            log_output("Warning: generate_evt not generating anything", log_level=0)
        ardname = world.lower()+room.lower()
        evtfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "evt.script")
        with open(evtfn) as f:
            script = AreaDataScript(f.read())
        programs_to_edit = script.programs if programnumber=="all" else {programnumber: script.programs[programnumber]}
        for currentprogramnumber, program in programs_to_edit.items():
            if not program.has_command("AreaSettings"):
                continue
            if "jump_to" in options:
                program.set_jump(options["jump_to"]["world"], options["jump_to"]["room"], options["jump_to"]["program"], set_for_settings=options["jump_to"].get("set_for_settings", None))
            if "open_menu" in options:
                program.set_open_menu(options["open_menu"])
            if "remove_event" in options:
                program.remove_event()
            if "remove_excess_flags" in options:
                program.remove_command("SetProgressFlag")
            if "flags" in options:
                program.set_flags(options["flags"])
            if options.get("fix_source_area_settings"):
                program.set_area_settings(16, -1)
            if options.get("fix_fadetypes"):
                jumps = [_ser(j) for j in prg.get_command("SetJump", return_all=True)]
                for ji in range(len(jumps)):
                    j = jumps[ji]
                    j.set_jump(jumptype=j["Type"], world=j["World"], room=j["Area"], entrance=j["Entrance"], program=j["LocalSet"], fadetype="1", set_for_settings=ji)
            programasset = self.modwriter.writeAreaDataProgram(ardname, "evt", currentprogramnumber, program.make_program())
            roomsource.append(programasset)

