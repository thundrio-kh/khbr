import json, os
class MissionManager:
    def __init__(self, basepath):
        self.basepath = basepath
        self.msninfo = self.get_msninfo()

    def get_msninfo(self):
        with open(os.path.join(self.basepath, "msns.json")) as f:
            return json.load(f)