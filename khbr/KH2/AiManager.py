class AiManager:
    def __init__(self, modstring):
        self.modlines = modstring
        self.fn = self.get_fn()
        self.edits = self.get_edits()
        
    def get_fn(self):
        return self.modlines[0].split("# ")[1].strip()

    def get_edits(self):
        return  [{"offset": int(e.split(" ")[0], 16), "value": e.split(" ")[1]} for e in self.modlines if not e.startswith("#") and len(e) > 0]

    def modify_data(self, data):
        for mod in self.edits:
            # They have to be reversed
            data[mod["offset"]+3] = int(mod["value"][:2], 16)
            data[mod["offset"]+2] = int(mod["value"][2:4], 16)
            data[mod["offset"]+1] = int(mod["value"][4:6], 16)
            data[mod["offset"]] = int(mod["value"][6:8], 16)