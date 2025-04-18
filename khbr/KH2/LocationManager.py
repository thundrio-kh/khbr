import json, os, yaml
from khbr.KH2.schemas.random_config import RandomConfig
from khbr._config import DEBUG_LOCATIONS
class LocationManager:
    def __init__(self, basepath):
        self.basepath = basepath
        # TODO I think this means I don't need to do this anywhere else
        # TODO but also maybe will make things load really slow initially
        self.set_locmap()
        self.set_btlmap()
        self.set_locations()

    def _merge_dicts(self, dict1, dict2):
        for k, v in dict2.items():
            if isinstance(v, dict):
                dict1[k] = self._merge_dicts(dict1.get(k, {}), v)
            else:
                dict1[k] = v
        return dict1

    def set_locmap(self):
        with open(os.path.join(self.basepath, "location-ard-map.json")) as f:
            self.locmap = json.load(f)

    def set_btlmap(self):
        with open(os.path.join(self.basepath, "btl-ard-data.yml")) as f:
            self.btlmap = yaml.load(f, Loader=yaml.FullLoader)

    def get_sp_max_enemy_types(self, room, unit):
        max_types = self.btlmap[f"{self.locmap[room]}-{unit}"].get("max_variety", "NOT_FOUND")
        if max_types == "NOT_FOUND":
            print(f"WARNING: NOT FOUND max_variety FOR {room}")
            max_types = 3
        return max_types

    def get_sp_for_mission(self, room, unit):
        return self.btlmap[f"{self.locmap[room]}-{unit}"]["mission"]

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

    def update_locations(self, new_locations):
        self.locations = self._merge_dicts(self.locations, new_locations)

    def update_locmap(self, new_locmap):
        self.locmap = self._merge_dicts(self.locmap, new_locmap)

    def get_ardname(self, room):
        return self.locmap[room]

    @staticmethod
    def update_location(location, config: RandomConfig):
        memory_expansion = config.memory_expansion
        if "moose" in location and memory_expansion:
            for k in location["moose"]:
                location[k] = location["moose"][k]
