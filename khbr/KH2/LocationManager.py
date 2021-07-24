class LocationManager:
    def __init__(self, path):
        with open(path) as f:
            self.locmap = json.load(f)