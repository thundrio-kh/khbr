import json, os, yaml
from khbr._config import DEBUG_LOCATIONS
class LocationManager:
    def __init__(self, basepath):
        self.basepath = basepath

    def set_locmap(self):
        with open(os.path.join(self.basepath, "location-ard-map.json")) as f:
            self.locmap = json.load(f)
    def set_locations(self):
        with open(os.path.join(os.path.dirname(__file__), "locations.yaml")) as f:
            locations_f = yaml.load(f, Loader=yaml.FullLoader)
        if DEBUG_LOCATIONS:
            newlocations = {}
            for world in locations_f:
                for room in locations_f[world]:
                    if room in DEBUG_LOCATIONS:
                        if world not in newlocations:
                            newlocations[world] = {}
                        newlocations[world][room] = locations_f[world][room]
            locations_f = newlocations
        self.locations = locations_f

    @staticmethod
    def update_location(location, config: RandomConfig):
        unlimited_memory = config.unlimited_memory
        if "pc" in location and unlimited_memory:
            for k in location["pc"]:
                location[k] = location["pc"][k]