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
        ]
        self.ignore_ards = [
            "lk08.ard", # Entering jungle for second visit story crashes pcsx2
            "wi03.ard", # Beating WI causes the portal to not turn purple
            "dc05.ard", # Marluxias portal doesn't show up after beating WI
            "hb05.ard", # Causes you to be sent to SP instead of skipping it, and makes the HB portal send you to Data Demyx
            "tt32.ard", # Causes GOA Mod to not give out the weapons of each ally, preventing second visits from working
            "nm05.ard", # Fix vexens portal not showing up (likely an issue with the ard being a different size now)
            "ca16.ard" # Fix OG Larxene portal still showing up (issue with ard size)
            "hb26.ard" # Prevents third chest from showing up in GOA, and can cause incorrect portals to turn purple
        ]
        self.ignore_programs =  {
            "tt27.ard": ["0x02"], # Talking to yen sid
            "tt28.ard": ["0x02"], # changing to kh2 sora
            "tr01.ard": ["0x33"], # causes entering SP the second time to go to data larxene
            "hb09.ard": ["0x33"], # causes first cutscene in merlin to not fire
            # "hb05.ard": ["0x02", "0x05", "0x06", "0x08"], # Causes you to be sent to SP instead of skipped, and makes demyx portal real
            "eh20.ard": ["0x4a"]
        }
        # I have a check to not skip cutscenes with type > 100 because those tend to signify menu events
        # but sometimes (like with postgame cutscenes) these are real cutscenes that should be removed
        self.always_remove = {
            "eh20.ard": [
                "0x4A" # postgame
            ]
        }
        self.unskippable = []
        self.ignored = []
    def shouldIgnore(self, ard, program, eventtype, setsinventory, ismission):
        ignore = False
        if ard[:2] in self.ignore_worlds:
            ignore = True
        if ard in self.ignore_ards:
            ignore = True
        # NEEDED To make choosing weapons work
        if int(eventtype) >= 128 and not ard.startswith("eh") and not ard.startswith("es"):
            self.unskippable.append("{}-{}".format(ard,program))
            ignore = True
        if ard in self.ignore_programs:
            if program.strip() in self.ignore_programs[ard]:
                ignore = True
        if ard in self.always_remove:
            if program.strip() in self.always_remove[ard]:
                ignore = False
        # Maximum ignore set first, then go back and turn off for lower levels
        if self.level < 3 and setsinventory:
            ignore = False
        if self.level < 2 and ismission:
            ignore = False
        if ignore:
            self.ignored.append("{}-{}".format(ard,program.strip()))
        return ignore
        
    def removeCutscenes(self):
        for ardname in self.location_manager.locmap.values():
            ardasset = self.assetgenerator.find_asset(ardname+".ard", self.assetgenerator.getDefaultRoomAsset(ardname+".ard"))
            evtfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "evt.script")
            btlfn = os.path.join(KH2_DIR, "subfiles", "script", "ard", ardname, "btl.script")
            with open(evtfn) as f:
                evtscript = AreaDataScript(f.read())
            with open(btlfn) as f:
                btlscript = AreaDataScript(f.read())
            for num in evtscript.programs:
                evtprogram = evtscript.get_program(num)
                hascs = evtprogram.has_command("SetEvent")
                if not hascs:
                    continue
                eventtype = evtprogram.get_command("SetEvent").split(" ")[-1]
                if eventtype == "66": # Is theater cutscene can ignore
                    continue
                setsinventory = evtprogram.has_command("SetInventory")
                btlprogram = btlscript.get_program(num)
                ismission = bool(btlprogram.get_mission()) if btlprogram else False
                removecs = self.shouldIgnore(ardname, num, eventtype, setsinventory, ismission)
                if removecs:
                    evtprogram.remove_event()
                    prgasset = self.modwriter.writeAreaDataProgram(ardname, "evt", num, evtprogram.make_program())
                    ardasset["source"].append(prgasset)