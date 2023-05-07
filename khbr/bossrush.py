import shutil
import time, json, os, random, yaml
from khbr.KH2.AreaDataScript import AreaDataScript
from khbr.KH2.AssetGenerator import AssetGenerator
from khbr.KH2.KingdomHearts2 import KingdomHearts2
from khbr.KH2.ModWriter import ModWriter
from khbr.randomizer import Randomizer

supported_games = ["kh2"]

#TODO the ignore bosses should be allowed for boss_in_room selection just not starting_room stuff
IGNORE_BOSSES = ["Scar Ghost", "Lock", "Shock", "Barrel", "Shadow Roxas", "Shenzie", "Shenzie (1)", "Banzai", "Banzai (1)", "Ed", "Ed (1)", "Hades (Cups)", "Pete (Cups)",
"Cerberus (Cups)", "Blizzard Lord (Cups)", "Volcano Lord (Cups)", "Leon", "Leon (1)", "Leon (2)", "Leon (3)",
"Cloud", "Cloud (1)", "Cloud (2)", "Cloud (3)", "Yuffie", "Yuffie (1)", "Yuffie (2)", "Yuffie (3)",
"Tifa", "Tifa (1)", "Tifa (2)", "Tifa (3)",
"Hades Cups", "Pete Cups", "Cerberus Cups", "Blizzard Lord Cups", "Volcano Lord Cups",

# Missing Program
"Hercules", "Illuminator", "Setzer",

# Also for now get rid of the TT04 and TT05 bosses it's confusing
"Seifer", "Seifer (2)", "Seifer (3)", "Seifer (4)", "Vivi",

"Final Xemnas (Clone)", "Final Xemnas (Clone) (Data)", "Pete OC I"
]

ITEMS = {'Potion': '1', 'Hi-Potion': '2', 'Ether': '3', 'Elixir': '4', 'Mega-Potion': '5', 'Mega-Ether': '6', 'Megalixir': '7', 'Ability Ring': '8', "Engineer's Ring": '9', "Technician's Ring": '10', "Expert's Ring": '11', 'Sardonyx Ring': '12', 'Tourmaline Ring': '13', 'Aquamarine Ring': '14', 'Garnet Ring': '15', 'Diamond Ring': '16', 'Silver Ring': '17', 'Gold Ring': '18', 'Platinum Ring': '19', 'Mythril Ring': '20', 'Fire Element': '21', 'Blizzard Element': '22', 'Thunder Element': '23', 'Cure Element': '24', 'Ukulele Charm (Summon Stitch)': '25', 'Valor Form': '26', 'Wisdom Form': '27', 'Orichalcum Ring': '28', 'Final Form': '29', 'Anti-Form': '30', 'Master Form': '31', 'Torn Pages': '32', "Master's Ring": '34', 'Moon Amulet': '35', 'Star Charm': '36', 'Skill Ring': '38', 'Skillful Ring': '39', 'Soldier Earring': '40', 'Kingdom Key': '41', 'Oathkeeper': '42', 'Oblivion': '43', 'Detection Saber': '44', 'Edge of Ultima': '45', 'Fencer Earring': '46', 'Mage Earring': '47', 'Slayer Earring': '48', "Knight's Shield": '49', 'Detection Shield': '50', 'Test The King (Shield)': '51', 'Cosmic Ring': '52', 'Medal': '53', 'Battlefields of War': '54', 'Sword of Ancestors': '55', 'Cosmic Arts': '56', 'Shadow Archive': '57', 'Shadow Archive+': '58', 'Lucky Ring': '63', 'Full Bloom': '64', 'Draw Ring': '65', 'Full Bloom+': '66', 'Elven Bandanna': '67', 'Divine Bandanna': '68', 'Power Band': '69', 'Buster Band': '70', 'Protect Belt': '78', 'Gaia Belt': '79', 'FAKE (looks like Sword of the Ancestors)': '80', 'FAKE (Keyblade,looks like Kingdom Key)': '81', 'Guard': '82', 'Magnet Element': '87', 'Reflect Element': '88', 'High Jump LV1': '94', 'High Jump LV2': '95', 'High Jump LV3': '96', 'High Jump MAX': '97', 'Quick Run LV1': '98', 'Quick Run LV2': '99', 'Quick Run LV3': '100', 'Quick Run MAX': '101', 'Aerial Dodge LV1': '102', 'Aerial Dodge LV2': '103', 'Aerial Dodge LV3': '104', 'Aerial Dodge MAX': '105', 'Glide LV1': '106', 'Glide LV2': '107', 'Glide LV3': '108', 'Glide MAX': '109', 'Cosmic Belt': '111', 'Tent': '131', 'Shock Charm': '132', 'Shock Charm+': '133', 'Upper Slash': '137', 'Scan': '138', 'Grand Ribbon': '157', 'Aerial Recovery': '158', 'Lamp Charm (Summon Genie)': '159', 'Feather Charm (Summon Peter Pan)': '160', 'Combo Plus': '162', 'Air Combo Plus': '163', 'Fire Bangle': '173', 'Fira Bangle': '174', 'Firaga Bangle': '197', 'Trinity Limit': '198', 'Slapshot': '262', 'Dodge Slash': '263', 'Slide Dash': '264', 'Guard Break': '265', 'Explosion': '266', 'Finishing Leap': '267', 'Counterguard': '268', 'Aerial Sweep': '269', 'Aerial Spiral': '270', 'Horizontal Slash': '271', 'Aerial Finish': '272', 'Retaliating Slash': '273', 'Drive Recovery': '274', 'High Drive Recovery': '275', 'Power Boost': '276', 'Magic Boost': '277', 'Defense Boost': '278', 'AP Boost': '279', 'Dark Shard': '280', 'Dark Stone': '281', 'Dark Gem': '282', 'Dark Crystal': '283', 'Firagun Bangle': '284', 'Blizzard Armlet': '286', 'Blizzara Armlet': '287', 'Blizzaga Armlet': '288', 'Blizzagun Armlet': '289', 'Thunder Trinket': '291', 'Thundara Trinket': '292', 'Thundaga Trinket': '293', 'Thundagun Trinket': '294', 'Shadow Anklet': '296', 'Dark Anklet': '297', 'Midnight Anklet': '298', 'Chaos Anklet': '299', 'Abas Chain': '301', 'Aegis Chain': '302', 'Acrisius': '303', 'Ribbon': '304', 'Champion Belt': '305', 'Petit Ribbon': '306', 'Acrisius+': '307', 'Cosmic Chain': '308', 'Baseball Charm (Summon Chicken Little)': '383', 'Struggle Sword': '384', 'Auto Valor': '385', 'Auto Wisdom': '386', 'Auto Master': '387', 'Auto Final': '388', 'Auto Summon': '389', 'Combo Boost': '390', 'Air Combo Boost': '391', 'Reaction Boost': '392', 'Finishing Plus': '393', 'Negative Combo': '394', 'Berserk Charge': '395', 'Damage Drive': '396', 'Drive Boost': '397', 'Form Boost': '398', 'Summon Boost': '399', 'Combination Boost': '400', 'Experience Boost': '401', 'Leaf Bracer': '402', 'Magic Lock-On': '403', 'No Experience': '404', 'Draw': '405', 'Jackpot': '406', 'Lucky Lucky': '407', 'Fire Boost': '408', 'Blizzard Boost': '409', 'Thunder Boost': '410', 'Item Boost': '411', 'MP Rage': '412', 'MP Haste': '413', 'Defender': '414', 'Second Chance': '415', 'Once More': '416', 'Auto Limit (I)': '417', 'Auto Change': '418', 'Hyper Healing': '419', 'Auto Healing': '420', 'MP Hastera': '421', 'MP Hastega': '422', 'Star Seeker': '480', 'Hidden Dragon': '481', 'Save the Queen': '482', 'Save The King': '483', "Hero's Crest": '484', 'Monochrome': '485', 'Follow the Wind': '486', 'Circle of Life': '487', 'Photon Debugger': '488', 'Gull Wing': '489', 'Rumbling Rose': '490', 'Guardian Soul': '491', 'Wishing Lamp': '492', 'Decisive Pumpkin': '493', 'Sleeping Lion': '494', 'Sweet Memories': '495', 'Mysterious Abyss': '496', 'Fatal Crest': '497', 'Bond of Flame': '498', 'Fenrir': '499', 'Ultima Weapon': '500', 'Struggle Wand': '501', 'Struggle Hammer': '502', 'Combo Master': '539', 'Drive Converter': '540', 'Light & Darkness': '541', 'Damage Control': '542', 'Two Become One': '543', "Winner's Proof": '544', 'Flash Step': '559', 'Aerial Dive': '560', 'Magnet Burst': '561', 'Vicinity Break': '562', 'Limit Form': '563', 'Dodge Roll LV1': '564', 'Dodge Roll LV2': '565', 'Dodge Roll LV3': '566', 'Dodge Roll MAX': '567', "Executive's Ring": '599'}

# Find my original plan for this and add in the actual routes

ROUTES = {
    "compatability-test": [
        "Armor Xemnas I",
        "Armor Xemnas II",
        "Axel I",
        "Axel II",
        "Barbossa", 
        "Cerberus",
        "Cerberus (Cups)",
        "Dark Thorn",
        "Demyx",
        "Demyx OC", # Infinite load end of fight
        "Final Xemnas",
        "Grim Reaper I",
        "Grim Reaper II",
        "Groundshaker", # Pete is slightly in the ground
        "Hades I", 
        "Hades Escape", # Pete can die
        "Hades II (1)",
        "Hayner",
        "Hostile Program", 
        "Hydra",
        "Larxene",
        "Luxord",
        "Marluxia",
        "Oogie Boogie",
        "Past Pete",
        "Pete OC II",
        "Pete TR",
        "Prison Keeper",
        "Riku",
        "Roxas",
        "Saix",
        "Sark",
        "Scar",
        "Seifer (1)",
        "Sephiroth",
        "Shan-Yu",
        "Storm Rider",
        "Terra",
        "The Beast",
        "The Experiment",
        "Thresholder",
        "Twilight Thorn",
        "Vexen",
        "Xaldin", 
        "Xemnas",
        "Xigbar",
        "Zexion",
        "Jafar",
        "MCP",
    ]
}

if os.path.exists("custom.route"):
    ROUTES["Custom"] = open("custom.route").read().split("\n")
class bossrush:
    def __init__(self, game, options, seed=None):
        if game not in supported_games:
            raise Exception("Game not supported")
        self.game = game
        self.options = options
        if not seed:
            self.seed = str(int(time.time()))

from gooey import Gooey, GooeyParser

@Gooey(program_name="Kingdom Hearts 2 Boss Rush/Tester")
def main_ui():
    main()

def main(cli_args: list=[]):
    last_settings = {
        "boss_in_room": "vanilla",
        "starting_room": "random",
        "num_bosses": 1,
        "level": 50,
        "route": 'random',
        "abilities_start_equipped": True,
        "randomize_starting_stuff": False,
        "platform": "pc",
        "open_menu_before_each_fight": False,
        "seed": "",
        "debug_inf_hp": False
    }
    default_config = {
        "openkh_dir": ""
    }
    if os.path.exists("last_settings.json"):
        last_settings = json.load(open("last_settings.json"))
    if os.path.exists("config.json"):
        default_config = json.load(open("config.json"))

    parser = GooeyParser()

    options = parser.add_argument_group(
        "Options",
        """prototype boss rush mod
    selected boss replacement
    start in selected boss room
    start with good stuff for combat
    winning the fight is seed over
    """
    )

    print(last_settings)

    kh2 = KingdomHearts2()
    source_bosses = kh2.get_valid_bosses()
    bosses = [b for b in source_bosses if b not in IGNORE_BOSSES]
    options.add_argument("-boss_in_room", choices=["vanilla", "random"] + bosses, default=last_settings.get("boss_in_room"))
    options.add_argument("-starting_room", choices=["default", "random"] + source_bosses, default=last_settings.get("starting_room"))
    options.add_argument("-num_bosses", choices=["random"] + [str(l) for l in range(1,len(bosses))], default=last_settings.get("num_bosses"))
    options.add_argument("-level", choices=["random"] + [str(l) for l in range(1,99)], default=last_settings.get("level"))
    options.add_argument("-route", choices=["random"] + list(ROUTES.keys()), default=last_settings.get("route"))
    options.add_argument("-randomize_starting_stuff", choices=['True', 'False'], default=last_settings.get("randomize_starting_stuff"))
    options.add_argument("-abilities_start_equipped", choices=['True', 'False'], default=last_settings.get("abilities_start_equipped"))
    options.add_argument("-open_menu_before_each_fight", choices=['True', 'False'], default=last_settings.get("open_menu_before_each_fight"))
    options.add_argument("-platform", choices=["ps2", "pc"], default=last_settings.get("platform"))
    options.add_argument("-seed", default=last_settings.get("seed"))
    options.add_argument("-debug_inf_hp", default=last_settings.get("debug_inf_hp"), choices=['True', 'False'])

    options.add_argument("-openkh_dir", help="Path to OpenKH folder.", default=default_config.get("openkh_dir"), widget='DirChooser')

    # Parse and print the results
    if cli_args:
        args = parser.parse_args(cli_args)
    else:
        args = parser.parse_args()


    def _translate_bool(value):
        if value in ['True', True]:
            return True
        if value in ['False', False]:
            return False

    settings_to_write = {
        "boss_in_room": args.boss_in_room,
        "starting_room": args.starting_room,
        "num_bosses": args.num_bosses,
        "level": args.level,
        "route": args.route,
        "abilities_start_equipped": _translate_bool(args.abilities_start_equipped),
        "randomize_starting_stuff": _translate_bool(args.randomize_starting_stuff),
        "open_menu_before_each_fight": _translate_bool(args.open_menu_before_each_fight),
        "platform": args.platform,
        "debug_inf_hp": _translate_bool(args.debug_inf_hp),
        "seed": args.seed
    }
    config_to_write = {
        "openkh_dir": args.openkh_dir
    }
    json.dump(config_to_write, open("config.json", "w"))
    json.dump(settings_to_write, open("last_settings.json", "w"))

    seed_options = {
        "memory_expansion": True if args.platform == "pc" else False,
        "always_set_retry": True,
        "apply_better_stt": True
    }
    if args.boss_in_room != "vanilla":
        if args.boss_in_room == "random":
            seed_options["boss"] = "One to One"
        else:
            seed_options["selected_boss"] = args.boss_in_room
    
    seed = args.seed or str(int(time.time()))
    print("Using Seed {}".format(seed))
    random.seed(seed)
    

 
    starting_room = args.starting_room if args.starting_room != "random" else random.choice(bosses)
    set_level = int(args.level) if args.level != "random" else random.randint(1,99)
    if set_level < 1 or set_level > 99:
        raise Exception("level setting must be within 1-99")
    route = args.route
    if route == 'random':
        num_bosses = int(args.num_bosses) if args.num_bosses != "random" else random.randint(1,len(bosses))
    else:
        num_bosses = len(ROUTES[route])
    print("Picked Route: "+ route)
    abilities_start_equipped = _translate_bool(args.abilities_start_equipped)
    randomize_starting_stuff = _translate_bool(args.randomize_starting_stuff)

    open_menu_before_each_fight = _translate_bool(args.open_menu_before_each_fight)
    openkh_dir = args.openkh_dir
    debug_inf_hp = _translate_bool(args.debug_inf_hp)
    

    boss_order = []
    index = bosses.index(starting_room)
    if route == "random":
        boss_order = [random.choice(bosses) for _ in range(num_bosses)] # TODO this should not pick the same boss twice
    else:
        boss_order = ROUTES[route]
        if not starting_room == "default":
            if starting_room in boss_order:
                boss_order = boss_order[boss_order.index(starting_room):]
            else:
                boss_order = [starting_room] + boss_order
    if len(boss_order) > num_bosses:
        boss_order = boss_order[:num_bosses]

    if not randomize_starting_stuff:
        stuff = ["Scan","Explosion",
        "Guard",
        "Horizontal Slash", "Berserk Charge"] + \
        ["Aerial Recovery"] + \
        ["Finishing Plus" for _ in range(2)] + \
        ["Negative Combo" for _ in range(2)] + \
        ["Second Chance", "Once More"] + \
        ["Fire Element" for _ in range(2)] + \
        ["Magnet Element" for _ in range(2)] + \
        ["Reflect Element" for _ in range(2)] + \
        ["Thunder Element" for _ in range(2)] + \
        ["Final Form", "Limit Form", "Valor Form", "Master Form"] + \
        ["Decisive Pumpkin"] + \
        ["High Jump LV3", "Quick Run LV3", "Aerial Dodge LV3", "Glide LV3", "Dodge Roll LV3"] + \
        ["Wisdom Form", "Flash Step"]
        if os.path.exists("custom.stuff"):
            stuff = open("custom.stuff").read().split("\n")
        addvalue = 0 if not abilities_start_equipped else 0x8000
        stuff = [str(int(ITEMS[s]) + addvalue) for s in stuff]
        #TODO in my own testing I found 58 is the max number of items....
        if len(stuff) > 32:
            raise Exception("Error: Can't have more than 32 pieces of stuff")
        # Nonrandomized list is all magic at 'aga', all forms, scan, decisive pumpkin, second chance, once more, both negative combos, explosion, magnet splash, 2 combo and air combo boosts, finisher, magic lock on, 10 megaelixers,
    else:
        stuff = []
        MAXITEMS = 32
        pickitems = [int(i) for i in ITEMS.values()]
        for i in range(MAXITEMS):
            itemvalue = random.choice(pickitems)
            if abilities_start_equipped:
                itemvalue += 0x8000
            stuff.append(str(itemvalue))


    moddir = os.path.join(openkh_dir, "mods", "kh2")
    # TODO TEMP FOR FASTER TESTING
    if os.path.exists(os.path.join(moddir, "bossrush")):
        shutil.rmtree(os.path.join(moddir, "bossrush"))
    rando = Randomizer(tempdir=moddir, tempfn="bossrush", deletetmp=False)
    b64 = rando.generate_seed("kh2", seed_options, seed=seed)

    modyml_fn = os.path.join(moddir, "bossrush", "mod.yml")
    modyml = yaml.load(open(modyml_fn))

    modyml["title"] = "Boss Rush {}".format(seed)
    modyml["description"] = json.dumps(settings_to_write, indent=2)

    kh2 = KingdomHearts2()
    modwriter = ModWriter(os.path.join(moddir, "bossrush"))
    assetgenerator = AssetGenerator(modwriter, spawn_manager=kh2.spawn_manager, location_manager=kh2.location_manager, enemy_manager=kh2.enemy_manager, ispc=seed_options["memory_expansion"])
    assetgenerator.assets = modyml["assets"]

    assetgenerator.generatePlrp(hp=20, mp=100, ap=50, accessoryslt=3, armorslt=3, itemslt=3, items=stuff)

    def findRoomSource(assets, world, room):
        #TODO I'm pretty sure pass by reference will do what I want, but once it's generating the mod file, make sure the 'evt' files are in the mod yml (and check in assetgenerator)
        ardname = world.lower()+room.lower()+".ard"
        for a in assets:
            if a["name"].endswith(ardname):
                return a
        # Need a new asset
        newasset = {
            "name": "ard/us/{}".format(ardname),
            "method": "binarc",
            "source": []
        }
        assets.append(newasset)
        return newasset

    first_boss = kh2.enemy_manager.enemy_records[starting_room]

    def getworld(b):
        if b.get("msn"):
            return b["msn"][:2]
        # msn list is HE
        return "HE"
    def getroom(b):
        if b.get("msn"):
            r = b["msn"][2:4]
            if r.lower() != "_c":
                return r
        return "09" # Assume colosseum
    world = getworld(first_boss)
    room = getroom(first_boss)
    program = first_boss["program"]
    current_boss = first_boss
    # Have to lookup the world/rooms that the first boss is in
    asset = findRoomSource(modyml["assets"], "TT", "01")
    assetgenerator.generateEvt("TT", "01", 0x34, asset["source"], options={"jump_to":{"world":world, "room":room, "program":program}, "open_menu":True, "remove_event":True, "flags": ['0x84A'], "remove_excess_flags": True})

    print("DEBUG boss_order {}".format(boss_order))
    boss_order.pop(0)

    for new_boss_name in boss_order:
        new_boss = kh2.enemy_manager.enemy_records[new_boss_name]
        newworld = getworld(new_boss)
        newroom = getroom(new_boss)
        newprogram = new_boss["program"] 
        if newprogram == None:
            newprogram = 0
            print("Warning setting program to 0 for {}".format(current_boss))
        asset = findRoomSource(modyml["assets"], world, room)
        print("Making evt to jump to {}".format(new_boss["name"]))
        set_for_settings = [1] if current_boss.get("name") in ["Hayner", "Vivi", "Setzer"] else None
        assetgenerator.generateEvt(world, room, current_boss.get("outprogram") or "all", asset["source"], options={"remove_event": True, "jump_to":{"world": newworld, "room": newroom, "program": newprogram, "set_for_settings": set_for_settings}, "fix_area_settings": "fix_area_settings" in current_boss.get("tags"), "open_menu": open_menu_before_each_fight, "remove_event":True})
        world = newworld
        room = newroom
        program = newprogram
        current_boss = new_boss
    
    asset = findRoomSource(modyml["assets"], world, room)
    assetgenerator.generateEvt(world, room, "all", asset["source"], options={"remove_event": True, "jump_to":{"world": "ES", "room": "00", "program": 69}, "fix_area_settings": "fix_area_settings" in current_boss.get("tags")})

    data_folder = os.path.join(os.path.dirname(__file__), "KH2", "data")

    # Need a special battle to make a colloseum boss rush battle work
    # TODO this won't work super well for generic boss rush, only for compatability testing
    asset = findRoomSource(modyml["assets"], "HE", "09")
    asset["source"] = [s for s in asset["source"] if not s["method"] == "copy"]
    new_program_text = open(os.path.join(os.path.dirname(__file__), "KH2", "data", "he09_bossrush_single.areadataprogram")).read()
    he_script = AreaDataScript(new_program_text, ispc=args.platform == "pc")
    he_prg = he_script.programs[0xc4]
    if args.platform == "pc":
        he_prg.add_packet_spec()
        he_prg.add_enemy_spec()
    programasset = assetgenerator.modwriter.writeAreaDataProgram("he09", "btl", 0xc4, he_prg.make_program())
    asset["source"].append(programasset)

    lua_content = open(os.path.join(data_folder, "bossrush.lua")).read()
    luaasset = assetgenerator.modwriter.writeLua("bossrush.lua", lua_content)

    modyml["assets"].append(luaasset)

    for asset in modyml["assets"]:
        if asset["name"].endswith("00battle.bin"):

            # Prevent form levelups
            fmlv = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data", "fmlvVanilla.yml")))
            for form in fmlv:
                for level in fmlv[form]:
                    level["Experience"] = 9999
                    level["Ability"] = 0
            fmlv_asset = assetgenerator.modwriter.writeFmlv(fmlv)
            asset["source"].append(fmlv_asset["source"][0])

            # Prevent get bonuses
            bons = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data", "bonsVanilla.yml")))
            for l,bon in bons.items():
                for c,char in bon.items():
                    char["AccessorySlotUpgrade"] = 0
                    char["ArmorSlotUpgrade"] = 0
                    char["BonusItem1"] = 0
                    char["BonusItem2"] = 0
                    char["DriveGaugeUpgrade"] = 0
                    char["HpIncrease"] = 0
                    char["ItemSlotUpgrade"] = 0
                    char["MpIncrease"] = 0
            bons_asset = assetgenerator.modwriter.writeBons(bons)
            asset["source"].append(bons_asset["source"][0])

            # effectively set level to choice
            lvup = yaml.load(open(os.path.join(os.path.dirname(__file__), "KH2", "data", "lvupVanilla.yml")))
            print("Setting all level stats to that of level {}".format(set_level))
            for c, char in lvup.items():
                lvl_stats = char[set_level]
                for l, level in char.items():
                    for k in level:
                        level[k] = lvl_stats[k]
                    level["Exp"] = 9999
                    level["ShieldAbility"] = 0
                    level["SwordAbility"] = 0
                    level["StaffAbility"] = 0
            lvup_asset = assetgenerator.modwriter.writeLvup(lvup)
            asset["source"].append(lvup_asset["source"][0])

    if debug_inf_hp:
        hp_lua = open(os.path.join(data_folder, "inf_hp.lua")).read()
        luaasset = assetgenerator.modwriter.writeLua("inf_hp.lua", hp_lua)
        modyml["assets"].append(luaasset)

    # starting weapons
    bincontent = open(os.path.join(os.path.dirname(__file__), "KH2", "data", "bin", "00common.bin"), "rb").read()
    commonasset = assetgenerator.modwriter.writeBin(bincontent, "00common.bdx", "00common.bin")
    modyml["assets"].append(commonasset)

    yaml.dump(modyml, open(modyml_fn, "w"))

    print("All Done!")

if __name__ == "__main__":
    import sys
    main()
    # if "cmd" in sys.argv:
    #     main()
    # else:
    #     main_ui()
