import json
class MissionManager:
    def __init__(self, basepath):
        self.basepath = basepath
    def set_msninfo(self):
        with open(self.basepath) as f:
            self.msninfo = json.load(f)