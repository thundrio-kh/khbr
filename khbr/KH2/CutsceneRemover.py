import os
from khbr.KH2.AreaDataScript import AreaDataScript
from khbr._config import KH2_DIR
from khbr.randutils import log_output

class CutsceneRemover:
    def __init__(self, assetgenerator, mode):
        self.assetgenerator = assetgenerator
        self.location_manager = assetgenerator.location_manager
        self.level = {
            'False': 0,
            'True': 1
        }[mode]
        self.cutscenes = {
            "0frame": open(os.path.join(os.path.dirname(__file__), "data", "bin", "0frame.event"), "rb").read(), # For everything else
            "6frame": open(os.path.join(os.path.dirname(__file__), "data", "bin", "6frame.event"), "rb").read(), # For for party member popups
            "10frame": open(os.path.join(os.path.dirname(__file__), "data", "bin", "10frame.event"), "rb").read(), # For cutscenes before popups
            "20frame": open(os.path.join(os.path.dirname(__file__), "data", "bin", "20frame.event"), "rb").read() # For cutscenes before popups
        }
        self.ignore_worlds = [
            "lm"
        ]
        self.ignore_ards = [
        ]
        self.ignore_programs =  {
        }
        # This should be world specific too TODO
        self.set_cutscene_for_event = {
            "701": "6frame",
            "617": "6frame",
            "616": "6frame",
            "615": "6frame",
            "614": "6frame",
            "613": "6frame"
        }
        self.only_type_66_cutscenes = ['106v', '103s', '107s', '117s', '117v', '302s', '202v', '204v', '104s', '104v', '208s', '206s', '110s', '110v', '109v', '202s', '204s', '106s', '121s', '316s', '212s', '116v', '516s', '111s', '801', '605s', '421s', '301s', '303v', '406v', '510s', '907s', '416s', '123v', '126s', '124s', '125v', '140s', '201s', '103v', '118s', '208v', '137s', '105v', '130v', '108s', '203s', '205s', '402s', '402v', '301v', '303s', '411s', '501v', '404s', '211s', '210s', '119s', '203v', '400s', '600', '100s', '600s', '100', '400', '200', '200s', '304s', '502v', '308v', '206v', '261a', '261b', '277v', '505s', '115v', '004s', '300', '300s', '311', '113s', '115s', '114s']
        self.always_remove = {
        }
        self.unskippable = []
        self.written_cutscenes = set()
    def shouldRemove(self, ard, program, ismission, eventnum, eventtype, full_event_list):
        if ard[:2] in self.ignore_worlds:
            return False
        if ard in self.ignore_ards:
            return False
        # NEEDED To make choosing weapons work
        # if int(eventtype) >= 128 and not ard.startswith("eh") and not ard.startswith("es"):
        #     return False
        if ard in self.ignore_programs:
            if program in self.ignore_programs[ard]:
                return False
        if ard[:2] == "lm":
            if ismission:
                return False
        if eventnum in self.only_type_66_cutscenes:
            return True
        if eventtype == "66":
            # if found this is theater cutscene can ignore
            for evinfo in full_event_list:
                ev_num = evinfo[-1]
                ev_type = evinfo[0].replace('"', '')
                if ev_num == eventnum and int(ev_type) != 66:
                    return False
        if ard in self.always_remove:
            if program in self.always_remove[ard]:
                return True
        return True
    def get_cutscene_name(self, program, eventnum, eventtype):
        if eventnum in self.set_cutscene_for_event:
            return self.set_cutscene_for_event[eventnum]
        if program.has_command("SetInventory"):
            return "10frame"
        if program.has_command("SetMember"):
            return "6frame"
        if int(eventtype) == 66:
            return "6frame" # I think this would also be fixed with a fadetype change
        if int(eventtype) == 67:
            return "6frame"
        for jump in program.get_command("SetJump", return_all=True):
            if "FadeType 16386" in jump:
                return "6frame" # TODO I think changing the fadetype would be key to stopping the random flashes and also making everything a 0 frame, something to mess with at a later time
        return "0frame"
    # Another TODO: Write logic to main a list to reference of all the chains of cutscenes, and if they were going to be rewritten what flags/etc would be used
    def removeCutscenes(self):

        def _writeEventFile(ardasset, new_cutscene_name, eventnum):
            new_cutscene = self.cutscenes[new_cutscene_name]
            eventasset = self.assetgenerator.modwriter.writeEvent(eventnum, new_cutscene_name, new_cutscene, write=new_cutscene_name in self.written_cutscenes)
            self.written_cutscenes.add(new_cutscene_name)
            ardasset["source"].append(eventasset)
        # TODO to get rid of the type 66 cutscenes in STT that matter, make a mapping of all cutscenes and their type, for ones that only have a type66 and not something else, add to always remove
        mapping = {}
        for ardname in self.location_manager.locmap.values():
            ardasset = self.assetgenerator.find_asset(ardname+".ard", self.assetgenerator.getDefaultRoomAsset(ardname))
            evtfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "evt.script")
            evtfn_goa = os.path.join(os.path.dirname(__file__), "data", "goa", "ard", ardname, "evt.script")
            btlfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "btl.script")
            evtscript_goa = None
            if not os.path.exists(evtfn):
                continue
            if os.path.exists(evtfn_goa):
                with open(evtfn_goa) as f:
                    evtscript_goa = AreaDataScript(f.read())
            with open(evtfn) as f:
                evtscript = AreaDataScript(f.read())
            hasbattle = os.path.exists(btlfn)
            if hasbattle:
                with open(btlfn) as f:
                    btlscript = AreaDataScript(f.read())
            for num in evtscript.programs:
                evtprogram = None
                if evtprogram:
                    evtscript = evtscript_goa.get_program(num)
                if not evtprogram:
                    evtprogram = evtscript.get_program(num)
                hascs = evtprogram.has_command("SetEvent")
                if not hascs:
                    continue
                events_list = evtprogram.get_command("SetEvent", return_all=True)
                for eventinfo in events_list:
                    eventinfo = eventinfo.split(" ")
                    eventtype = eventinfo[-1]
                    eventnum = eventinfo[0].replace('"', '')
                    if eventnum not in mapping:
                        mapping[eventnum] = set()
                    mapping[eventnum].add(eventtype)
                    if hasbattle:
                        btlprogram = btlscript.get_program(num)
                        ismission = bool(btlprogram.get_mission()) if btlprogram else False
                    else:
                        ismission = False
                    removecs = self.shouldRemove(ardname, num, ismission, eventnum, eventtype, events_list)
                    if removecs:
                        new_cutscene_name = self.get_cutscene_name(evtprogram, eventnum, eventtype)
                        _writeEventFile(ardasset, new_cutscene_name, str(eventnum))

            # This isn't getting picked up atm because my areadataprogram parser only parses the first areadatasettings in a program
            # so hack with a TODO to fix
            if "tt04" in ardasset["name"]:
                _writeEventFile(ardasset, "0frame", str(110))
                _writeEventFile(ardasset, "0frame", str(111))


        # l = []
        # for k,v in mapping.items():
        #     if v == {'66'}:
        #         l.append(k)
        #log_output(l)

# 2 issues
# ard.ard
# lm only