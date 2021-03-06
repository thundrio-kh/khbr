import time, json

supported_games = ["kh2"]

class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "01"
        self.name = "kh2"
    def get_valid_enemies(self):
        return ["Air Pirate"]
    def get_valid_bosses(self):
        return ["Marluxia"]
    def get_options(self):
        return {
            "enemy": ["one_to_one", "spawnpoint_one_to_one", "wild"],
            "selected_enemy": self.get_valid_enemies(),
            "bosses_can_replace_enemies": [True, False],
            "nightmare_enemies": [True, False],
            "separate_small_big_enemies": [True, False],
            "scale_enemy_stats": [True, False],

            "memory_expansion": [True, False],

            "boss": ["one_to_one", "duplicates_allowed"],
            "nightmare_bosses": [True, False],
            "scale_boss_stats": [True, False],
            "stable_bosses_only": [True, False],
            "selected_boss": self.get_valid_bosses()
        }

class Randomizer:
    def __init__(self):
        pass

    def _get_game(self, game):
        if game == "kh2":
            return KingdomHearts2()

    def _validate_options(self, schema, options):
        if type(options) not in [dict, str]:
            raise Exception("Invalid type for options: {}".format(type(options)))
        elif type(options) == str:
            options = json.loads(options)
        for key in options:
            if key not in schema:
                raise Exception("Option {} is not a valid option".format(key))
            else:
                if options[key] not in schema[key]:
                    raise Exception("Option {}-{} is not found in valid options: {}".format(key, options[key], schema[key]))
    
    def generate_filename(self, game, seed, options):
        if type(game) == str:
            game = self._get_game(game)
        name = game.name + "_" + game.schemaversion + "_" + seed + "_"
        validoptions = game.get_options()
        sortedkeys = sorted(validoptions.keys())
        translated = []
        for o in range(len(sortedkeys)):
            key = sortedkeys[o]
            if key in options:
                translated.append(str(o))
                translated.append( str(validoptions[key].index(options[key])) )
        name += '-'.join(translated)
        name += ".zip"
        return name

    def expand_filename(self, name):
        noextension = name
        if "." in name:
            noextension = name.split(".")[0]
        parts = noextension.split("_")
        if len(parts) != 4:
            raise Exception("Invalid Filename")
        gm = parts[0]
        if gm not in supported_games:
            raise Exception("Game not supported: {}".format(gm))
        game = self._get_game(gm)
        schema = parts[1]
        if schema != game.schemaversion:
            raise Exception("Invalid schema version {}: current version {}".format(schema, game.schemaversion))
        
        compressedoptions = parts[3].split("-")
        options = {}

        validoptions = game.get_options()
        sortedkeys = sorted(validoptions.keys())
        for i in range(0, len(compressedoptions), 2):
            key = sortedkeys[int(compressedoptions[i])]
            value = validoptions[key][int(compressedoptions[i+1])]
            options[key] = value

        seed = parts[2]
        return gm, seed, options

    def generate_seed(self, g, seed, options):
        if g not in supported_games:
            raise Exception("Game not supported")
        game = self._get_game(g)
        self._validate_options(game.get_options(), options)
        if not seed:
            self.seed = int(time.time())

if __name__ == '__main__':
    pass