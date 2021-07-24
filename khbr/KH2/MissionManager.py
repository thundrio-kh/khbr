class MissionManager:
    def __init__(self, path):
        with open(path) as f:
            self.msninfo = json.load(f)