class SpawnManager:
    def __init__(self):
        self.spawns = None
        self.roommodedits = {
            "ax2_99": self.ax2_99,
            "ax2_40": self.ax2_40,
            "ax2_50": self.ax2_50,
            "stormrider_61": self.stormrider_61
        }

    def set_spawns(self):
        if not self.spawns:
            self.spawns = self.get_locations()

    def modify_spawn(self, editname, spawnpoint):
        if editname not in self.roommodedits:
            print("Warning: could not find {} method for editing spawn, leaving unmodified".format(editname))
            return
        self.roommodedits(spawnpoint)

    def ax2_99(self, spawnpoint):
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

    def ax2_40(self, spawnpoint):
        # remove the buildings
        for spid in spawnpoint:
            spid["Entities"] = []

    def ax2_50(self, spawnpoint):
        # remove the dragon
        spawnpoint[0]["Entities"] = []

    def stormrider_61(self, spawnpoint):
        # move enemies height to the bottom
        sora = spawnpoint[0]["Entities"][0]
        sora["PositionY"] = 0

        donald = spawnpoint[0]["Entities"][1]
        donald["PositionY"] = 0

        goofy = spawnpoint[0]["Entities"][2]
        goofy["PositionY"] = 0

        boss = spawnpoint[0]["Entities"][3]
        boss["PositionY"] = 0