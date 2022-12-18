import os
from khbr.KH2.AreaDataScript import AreaDataScript
from khbr._config import KH2_DIR
class CutsceneRemover:
    def __init__(self, assetgenerator, mode):
        self.assetgenerator = assetgenerator
        self.location_manager = assetgenerator.location_manager
        self.level = {
            "Disabled": 0,
            "Minimal": 1,
            "Non-Reward": 2,
            "Maximum": 3
        }[mode]
        self.ignore_worlds = [
            "lm", # little mermaid is all cutscenes lol so it softlocks
            "dc" # there are problems with not being able to enter the world right now, so hammer
        ]
        self.ignore_ards = [
            "lk08", # Entering jungle for second visit story crashes pcsx2
            "wi03", # Beating WI causes the portal to not turn purple
            "dc05", # Marluxias portal doesn't show up after beating WI
            "hb05", # Causes you to be sent to SP instead of skipping it, and makes the HB portal send you to Data Demyx
            "tt32", # Causes GOA Mod to not give out the weapons of each ally, preventing second visits from working
            "nm05", # Fix vexens portal not showing up (likely an issue with the ard being a different size now)
            "ca16", # Fix OG Larxene portal still showing up (issue with ard size)
            "hb26", # Prevents third chest from showing up in GOA, and can cause incorrect portals to turn purple
            "dc06" # first cutscene in dc
        ]
        self.ignore_programs =  {
            "tt27": [0x02], # Talking to yen sid
            "tt28": [0x02], # changing to kh2 sora
            "tr01": [0x33], # causes entering SP the second time to go to data larxene
            "hb09": [0x33], # causes first cutscene in merlin to not fire
            # "hb05.ard": ["0x02", "0x05", "0x06", "0x08"], # Causes you to be sent to SP instead of skipped, and makes demyx portal real
            "eh20": [0x4a],
            "po00": [0x0a], # leaving 100 acre
            "al10": [0x3A], # leaving treasure room
            # fix losing keyblades when leaving stt
            "tt04": [0x4C, 0x4D, 0x4E, 0x4F],
            "tt05": [0x54, 0x55, 0x58],
            "tt14": [0x7f]
        }
        # I have a check to not skip cutscenes with type > 100 because those tend to signify menu events
        # but sometimes (like with postgame cutscenes) these are real cutscenes that should be removed
        self.always_remove = {
            "eh20": [
                0x4A # postgame
            ]
        }
        self.unskippable = []
    def shouldRemove(self, ard, program, eventtype, setsinventory, ismission):
        if ard[:2] in self.ignore_worlds:
            return False
        if ard in self.ignore_ards:
            return False
        # NEEDED To make choosing weapons work
        if int(eventtype) >= 128 and not ard.startswith("eh") and not ard.startswith("es"):
            return False
        if ard in self.ignore_programs:
            if program in self.ignore_programs[ard]:
                return False
        if ard in self.always_remove:
            if program in self.always_remove[ard]:
                return True
        # Maximum ignore set first, then go back and turn off for lower levels
        if self.level < 3 and setsinventory:
            return False
        if self.level < 2 and ismission:
            print(ard, program)
            return False
        return True
        
    def removeCutscenes(self):
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
                eventtype = evtprogram.get_command("SetEvent").split(" ")[-1]
                if eventtype == "66": # Is theater cutscene can ignore
                    continue
                setsinventory = evtprogram.has_command("SetInventory")
                if hasbattle:
                    btlprogram = btlscript.get_program(num)
                    ismission = bool(btlprogram.get_mission()) if btlprogram else False
                else:
                    ismission = False
                removecs = self.shouldRemove(ardname, num, eventtype, setsinventory, ismission)
                if removecs:
                    evtprogram.remove_event()
                    prgasset = self.assetgenerator.modwriter.writeAreaDataProgram(ardname, "evt", num, evtprogram.make_program())
                    ardasset["source"].append(prgasset)

# 2 issues
# ard.ard
# lm only