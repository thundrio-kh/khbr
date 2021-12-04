import json, os, yaml
from khbr.KH2.schemas.random_config import RandomConfig
from khbr._config import DEBUG_LOCATIONS
class LocationManager:
    def __init__(self, basepath):
        self.basepath = basepath
        # TODO I think this means I don't need to do this anywhere else
        # TODO but also maybe will make things load really slow initially
        self.set_locmap()
        self.set_locations()

    def set_locmap(self):
        with open(os.path.join(self.basepath, "location-ard-map.json")) as f:
            self.locmap = json.load(f)
    def set_locations(self):
        with open(os.path.join(os.path.dirname(__file__), "data", "locations.yaml")) as f:
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
        memory_expansion = config.memory_expansion
        if "pc" in location and memory_expansion:
            for k in location["pc"]:
                location[k] = location["pc"][k]
