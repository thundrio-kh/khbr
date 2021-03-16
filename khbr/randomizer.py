import time, json, random, os, shutil, yaml, base64
from zipfile import ZipFile
import random

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
        # Might want to define valid predicates at some point, as certain combinations can't be selected together
        return {
            "enemy": ["one_to_one", "spawnpoint_one_to_one", "wild", False],
            "selected_enemy": self.get_valid_enemies(),
            "bosses_can_replace_enemies": [True, False],
            "nightmare_enemies": [True, False],
            "separate_small_big_enemies": [True, False],
            "scale_enemy_stats": [True, False],

            "memory_expansion": [True, False],

            "boss": ["one_to_one", "one_to_one_characters", "wild", False],
            "nightmare_bosses": [True, False],
            "scale_boss_stats": [True, False],
            "stable_bosses_only": [True, False],
            "selected_boss": self.get_valid_bosses()
        }
    def get_enemies(self):
        # Respect disabled flags and such
        pass
    def get_bosses(self):
        pass
    def get_locations(self):
        pass
    def filter_enemies(self, enemylist, attribute, isfalse=False)
        pass
    def add_tag(self, enemylist, tag):
        pass
    def remove_tag(self, enemylist, tag):
        pass
    def pickbossmapping(self, bosslist, bossmode, unlimited_memory=False):
        pass # Just doing the really stupid thing
    def pickenemymapping(self, enemylist):
        pass 
    def pick_boss_to_replace(self, oldname, bosslist, unlimited_memory=False):
        False
    def get_enemy_attribute(self, name, attribute):
        pass
    def pick_enemy_to_replae(self, oldname, enemylist):
        pass #Remember tags
    def perform_randomization(self, options):
        unlimited_memory = options["memory_expansion"] if "memory_expansion" in options else False
        scale_enemy, scale_boss = False
        selected_boss, selected_enemy = False
        enemies, bosses, duplicate_enemies, duplicate_bosses, bossmode, enemymode = None
        if "enemy" in options and options["enemy"]:
            enemymode = options["enemy"]
            duplicate_enemies = enemymode in ["spawnpoint_one_to_one", "wild"]
            enemies = self.get_enemies()
            if "scale_enemy_stats" in options:
                scale_enemy = options["scale_enemy_stats"]
            if "bosses_can_replace_enemies" in options and options["bosses_can_replace_enemies"]:
                # Might eventually want to limit this to 10% of replacements get a boss, see how it plays
                duplicate_enemies = True
                bossenemies = self.filter_enemies(self.get_bosses(), "can_be_enemy")
                bossenemies = self.filter_enemies(bossenemies, "unstable", isfalse=True)
                bossenemies = self.add_tag(bossenemies, "large")
                enemies = enemies + bossenemies
            if "nightmare_enemies" in options and options["nightmare_enemies"]:
                duplicate_enemies = True
                enemies = self.filter_enemies(enemies, "isnightmare")
            if not ("separate_small_big_enemies" in options and options["separate_small_big_enemies"]):
                enemies = self.remove_tag(enemies, "large")
            if "selected_enemy" in options and options["selected_enemy"]:
                enemymode = "wild"
                duplicate_enemies = True
                selected_enemy = options["selected_enemy"]
        if "boss" in options and options["boss"]:
            bossmode = options["boss"]
            duplicate_bosses = options["boss"] == "wild"
            bosses = self.get_bosses()
            if "scale_boss_stats" in options:
                scale_boss = options["scale_boss_stats"]
            if "stable_bosses_only" in options and options["stable_bosses_only"]:
                duplicate_bosses = True
                bosses = self.filter_enemies(bosses, "unstable", isfalse=True)
            if "nightmare_bosses" in options and options["nightmare_bosses"]:
                duplicate_bosses = True
                bosses = self.filter_enemies(bosses, "isnightmare")
            if "selected_boss" in options and options["selected_boss"]:
                bossmode = "wild"
                duplicate_bosses = True
                selected_boss = options["selected_boss"]
            
            bossmapping = self.pickbossmapping(bosses, bossmode, unlimited_memory) if not duplicate_enemies else None
            enemymapping = self.pickenemymapping(enemies) if not duplicate_bosses else None

            spawns = self.get_locations()
            spawn_limiters = {}
            msn_mapping = {}
            set_scaling = {}
            ai_mods = {}
            for w in spawns:
                world = spawns[w]
                for r in world:
                    room = world[r]
                    if "ignored" in room:
                        del spawns[w][r]
                        continue
                    if enemies and enemymode == "spawnpoint_one_to_one":
                        enemymapping = self.pickenemymapping(enemies)
                    for sp in room:
                        spawnpoint = room[sp]
                        for i in spawnpoint:
                            entities = spawnpoint[i]
                            for e in range(len(entities)):
                                ent = entities[e]
                                if ent["isboss"]:
                                    if not bosses:
                                        continue # Bosses aren't being randomized
                                    if selected_boss:
                                        new_boss = selected_boss
                                    elif bossmapping:
                                        new_boss = bossmapping[ent["name"]]
                                    else:
                                        new_boss = self.pick_boss_to_replace(ent["name"], bosses, unlimited_memory)
                                    if new_boss == ent["name"]:
                                        continue
                                    # Bosses don't have spawn limiters normally, so don't need to set them
                                    msn_mapping[self.getEnemyAttribute(ent["name"], "msn")] = self.getEnemyAttribute(new_boss, "msn")
                                    if scale_boss:
                                        if new_boss not in set_scaling:
                                            hp = self.getEnemyAttribute(ent["name"], "hp")
                                            level = self.getEnemyAttribute(ent["name"], "level")
                                            set_scaling[new_boss] = (hp, level)
                                        else:
                                            hp = self.getEnemyAttribute(ent["name"], "hp")
                                            level = self.getEnemyAttribute(ent["name"], "level")
                                            if hp > set_scaling[new_boss][0]:
                                                set_scaling[new_boss] = (hp, level)
                                    if self.getEnemyAttribute(new_boss, "aiMod"):
                                        # In some cases it might be useful to know who is being replaced,
                                        ## IE the height Axel spawns the fire floor might be different on a per room basis
                                        ai_mods[new_boss] = ent["name"]
                                else:
                                    if not enemies:
                                        continue
                                    if selected_enemy:
                                        new_enemy = selected_enemy
                                    elif enemymapping:
                                        new_enemy = enemymapping[ent["name"]]
                                    else:
                                        #Remember tags
                                        new_enemy = self.pick_enemy_to_replace(ent["name"], enemies)
                                    oldlimiter = self.getEnemyAttribute(ent["name"], "limiter")
                                    if new_enemy not in spawn_limiters:
                                        spawn_limiters[new_enemy] = oldlimiter
                                    else:
                                        spawn_limiters[new_enemy] = min(oldlimiter, spawn_limiters[new_enemy])
                                    if scale_enemy:
                                        if new_enemy not in set_scaling:
                                            set_scaling[new_enemy] = []
                                        set_scaling[new_enemy].append(ent["name"])

            return {"spawns": spawns, "msn_map": msn_mapping, "ai_mods": set(ai_mods), "scale_map": set_scaling, "limiter_map": spawn_limiters}
 


                

    def generate_mod_basics(self):
        return {"title": "KH2 Boss/Enemy Rando"}

class Randomizer:
    def __init__(self, tempdir=None):
        self.tempdir = tempdir or "C:\\temp"

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
    
    def _make_tmpdir(self):
        fn = os.path.join(self.tempdir, ''.join(list(str(random.randint(0,10)) for _ in range(7))))
        if os.path.exists(fn):
            # Realistically this should never happen
            raise Exception("TMP dir already exists, try again")
        os.mkdir(os.path.join(self.tempdir, fn))
        rmdir = lambda : shutil.rmtree(fn)
        return fn, rmdir

    def _create_yaml(self, fn, obj):
        yaml.dump(obj, open(fn, "w"))
    
    def _create_zip(self, moddir, fn):
        with ZipFile(fn, "w") as z:
            for folder, _, fns in os.walk(moddir):
                for wfn in fns:
                    pth = os.path.join(folder, wfn)
                    z.write(pth, wfn)
        with open(fn, "rb") as f:
            b64zip = base64.encodebytes(f.read())
        os.remove(fn)
        return b64zip

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
        fn = self.generate_filename(game, seed, options)
        if not seed:
            self.seed = int(time.time())
        mod_yaml = game.generate_mod_basics()
        moddir, rmmoddir = self._make_tmpdir()

        # for both enemies and bosses
        # replacements are either decided beforehand, or at the time of replacement
        random.seed(seed)
        randomization = game.perform_randomization(options)

        self._create_yaml(os.path.join(moddir, "mod.yml"), mod_yaml)
        zipped = self._create_zip(moddir, fn)

        rmmoddir()

        return zipped

if __name__ == '__main__':
    Randomizer().generate_seed("kh2", "1234", {"selected_enemy": "Air Pirate"})