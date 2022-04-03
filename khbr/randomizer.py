from khbr.KH2.KingdomHearts2 import KingdomHearts2
from khbr.textutils import create_spoiler_text
from khbr.utils import print_debug
import time, json, random, os, shutil, yaml, base64, sys
from zipfile import ZipFile
import random
from khbr._config import *

supported_games = ["kh2"]

class Randomizer:
    def __init__(self, tempdir=None, tempfn=None, deletetmp=True):
        self.tempdir = tempdir or "C:\\temp"
        self.tempfn = tempfn
        self.deletetmp=deletetmp

    def get_options_cli(self, game):
        options = game.get_options()
        options.update(game.get_hidden_options())
        return options

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
                if options[key] not in schema[key]["possible_values"] + schema[key]["hidden_values"]:
                    raise Exception("Option {}-{} is not found in valid options: {}".format(key, options[key], schema[key]))
    
    def _make_tmpdir(self):
        if self.tempfn:
            fn = os.path.join(self.tempdir, self.tempfn)
        else:
            fn = os.path.join(self.tempdir, ''.join(list(str(random.randint(0,10)) for _ in range(7))))
        if os.path.exists(fn):
            print_debug(fn)
            # Realistically this should never happen
            raise Exception("TMP dir already exists, try again")
        os.mkdir(fn)
        rmdir = lambda : shutil.rmtree(fn)
        return fn, rmdir

    def _create_yaml(self, fn, obj):
        with open(fn, "w") as f:
            yaml.dump(obj, f)
    
    def _create_zip(self, moddir, fn):
        # Creates a zip with too many paths
        with ZipFile(fn, "w") as z:
            for folder, _, fns in os.walk(moddir):
                for wfn in fns:
                    pth = os.path.join(folder, wfn)
                    z.write(pth, pth)
        with open(fn, "rb") as f:
            b64zip = base64.encodebytes(f.read())
        os.remove(fn)
        return b64zip

    def generate_filename(self, game, seed, options):
        if type(game) == str:
            game = self._get_game(game)
        name = game.name + "_" + game.schemaversion + "_" + seed + "_"
        validoptions = self.get_options_cli(game)
        sortedkeys = sorted(validoptions.keys())
        translated = []
        for o in range(len(sortedkeys)):
            key = sortedkeys[o]
            if key in options:
                translated.append(str(o))
                optionslist = validoptions[key]["possible_values"] + validoptions[key]["hidden_values"]
                translated.append( str(optionslist.index(options[key])) )
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

        validoptions = self.get_options_cli(game)
        sortedkeys = sorted(validoptions.keys())
        for i in range(0, len(compressedoptions), 2):
            key = sortedkeys[int(compressedoptions[i])]
            value = validoptions[key]["possible_values"][int(compressedoptions[i+1])]
            options[key] = value

        seed = parts[2]
        return gm, seed, options

    def _generate_images(self, fn, outdir):
        import pydenticon
        generator = pydenticon.Generator(10, 10)
        raw_image = generator.generate(fn, 128, 128, output_format="png")
        # image_stream = BytesIO(raw_image)
        with open(os.path.join(outdir, "icon.png"), "wb") as f:
            f.write(raw_image)
        
    def generate_mod(self, game, fn, randomization, newname=None, dumpspoilers=True):
        mod_yaml = game.generate_mod_basics(newname)
        moddir, rmmoddir = self._make_tmpdir()
        
        assets = game.generate_files(moddir, randomization)
        if dumpspoilers:
            if game.spoilers["boss"] or game.spoilers["enemy"]:
                with open(os.path.join(moddir, "spoilers.txt"), "w") as f:
                    f.write(create_spoiler_text(game.spoilers))
            else:
                with open(os.path.join(moddir, "spoilers.json"), "w") as f:
                    json.dump(randomization, f, indent=4)
        #print(create_spoiler_text(game.spoilers))
        mod_yaml["assets"] = assets
        self._create_yaml(os.path.join(moddir, "mod.yml"), mod_yaml)
        
        if GENERATE_IDENTICON:
            self._generate_images(fn, moddir)

        zipped = self._create_zip(moddir, fn)

        if self.deletetmp:
            rmmoddir()

        return zipped

    def read_seed(self, g, seedfn=False, seed=False, outfn="fn", spoilers=None):
        if g not in supported_games:
            raise Exception("Game not supported")
        if not (seedfn or seed):
            raise Exception("Need one of seedfn or seed")
        game = self._get_game(g)
        if spoilers:
            game.spoilers=spoilers
        if seed:
            randomization = seed
        else:
            with open(seedfn) as f:
                if seedfn.endswith("json"):
                    randomization = json.load(f)
                elif seedfn.endswith("yaml"):
                    randomization = yaml.load(f, Loader=yaml.SafeLoader)
                else:
                    raise Exception("Unsupported Seed Format! Need json or yaml")
        return self.generate_mod(game, outfn, randomization, newname=os.path.basename(outfn))

    # My zipped functionality is broken, as the mod randomizer wants just the files in the root of the zip
    def generate_seed(self, g, options, seed=None, randomization_only=False):
        if g not in supported_games:
            raise Exception("Game not supported")
        game = self._get_game(g)
        self._validate_options(self.get_options_cli(game), options)
        if not seed:
            seed = str(random.randint(0,100000))
        fn = self.generate_filename(game, seed, options)
        if not seed:
            self.seed = int(time.time())

        randomization = self.generate_randomization(game, options, seed)
        if randomization_only:
            return randomization

        zipped = self.read_seed(g, seed=randomization, outfn=fn, spoilers=game.spoilers)
        return zipped

    def generate_randomization(self, game, options, seed):
        # for both enemies and bosses
        # replacements are either decided beforehand, or at the time of replacement
        random.seed(seed)
        print("Using seed: {}".format(seed))
        randomization = game.perform_randomization(options, seed=seed)
        
        return randomization

    def generateToZip(self, g, options, modobj, outZip):
        if g not in supported_games:
            raise Exception("Game not supported")
        game = self._get_game(g)
        self._validate_options(self.get_options_cli(game), options)

        randomization = game.perform_randomization(options)
        assets = game.generate_files(randomization=randomization, outzip=outZip)
        for asset in assets:
            found = False
            for modobj_asset in modobj["assets"]:
                if modobj_asset["name"] == asset["name"]:
                    found = True
                    for source in asset["source"]:
                        modobj_asset["source"].append(source)
            if not found:
                modobj["assets"].append(asset)
        return create_spoiler_text(game.spoilers)
    
    def getSchemaForGame(self, g):
        if g not in supported_games:
            raise Exception("Game not supported")
        game = self._get_game(g)
        return self.get_options_cli(game)

if __name__ == '__main__':
    import time
    t = time.time()
    mode = sys.argv[1]
    # run randomizer.py devgenerate "{\"boss\": \"One to One\", \"enemy\": \"One to One\"}" randomization_only
    # run randomizer.py devgenerate "{\"boss\": \"Wild\", \"data_bosses\": true}"
    # run randomizer.py devgenerate "{\"boss\": \"Wild\", \"cups_bosses\": false, \"data_bosses\": false, \"scale_boss_stats\": true}"
    # run randomizer.py devgenerate "{\"selected_boss\": \"Barbossa\"}"
    # run randomizer.py devgenerate "{\"selected_enemy\": \"Dancer\"}"
    # run randomizer.py devgenerate "{\"enemy\": \"One to One\", \"combine_enemy_sizes\": true}"
    # run randomizer.py devgenerate "{\"boss\": \"One to One\", \"mickey_rule\": \"all\"}" randomization_only
    options = sys.argv[2]
    if len(sys.argv) > 3:
        seed = sys.argv[3]
    else:
        seed=None
    if options[0] == "{":
        options = json.loads(options)
    else:
        options = {}
        for arg in sys.argv:
            print_debug(arg)
            if "=" in arg:
                opt = arg.split("=")
                print_debug(opt)
                options[opt[0]] = opt[1]

    if "randomization_only" in sys.argv:
        randomization_only = True
    else:
        randomization_only = False

    if mode.startswith("dev"):
        # moddir = "/mnt/c/Users/15037/git/OpenKh/OpenKh.Tools.ModsManager/bin/debug/net5.0-windows/mods/thundrio-kh"
        #moddir = "C:\\Users\\Arcade\\Desktop\\git\\OpenKh\\OpenKh.Tools.ModsManager\\bin\\Debug\\net5.0-windows\\mods\\thundrio-kh"
        moddir = "C:\\Users\\12sam\\Desktop\\openkh\\mods\\thundrio-kh"
        fn = "devmod"
        if os.path.exists(os.path.join(moddir, fn)):
            shutil.rmtree(os.path.join(moddir, fn))
        mode = mode[3:]
    else:
        moddir = "/tmp"
        fn = None

    rando = Randomizer(tempdir=moddir, tempfn=fn, deletetmp=False)
    if mode == "read":
        print(options)
        b64 = rando.read_seed("kh2", seedfn=options["seed"], outfn=fn)
    else:
        b64 = rando.generate_seed("kh2", options, seed=seed, randomization_only=randomization_only)

    print("Total thing took {}s".format(time.time()-t))