import shutil
import time, json, os, random, yaml
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
"Hades II", "Hades", # Not sure but uggg
"Hades Cups", "Pete Cups", "Cerberus Cups", "Blizzard Lord Cups", "Volcano Lord Cups",

# Missing Program
"Hades I", "Hades II (1)", "Hayner", "Hercules", "Illuminator", "Setzer",

# Also for now get rid of the TT04 and TT05 bosses it's confusing
"Seifer", "Seifer (1)", "Seifer (2)", "Seifer (3)", "Seifer (4)", "Vivi", "Axel I",

"Final Xemnas (Clone)", "Final Xemnas (Clone) (Data)", "Pete OC I"
]

ITEMS = {'Potion': '1', 'Hi-Potion': '2', 'Ether': '3', 'Elixir': '4', 'Mega-Potion': '5', 'Mega-Ether': '6', 'Megalixir': '7', 'Ability Ring': '8', "Engineer's Ring": '9', "Technician's Ring": '10', "Expert's Ring": '11', 'Sardonyx Ring': '12', 'Tourmaline Ring': '13', 'Aquamarine Ring': '14', 'Garnet Ring': '15', 'Diamond Ring': '16', 'Silver Ring': '17', 'Gold Ring': '18', 'Platinum Ring': '19', 'Mythril Ring': '20', 'Fire Element': '21', 'Blizzard Element': '22', 'Thunder Element': '23', 'Cure Element': '24', 'Ukulele Charm (Summon Stitch)': '25', 'Valor Form': '26', 'Wisdom Form': '27', 'Orichalcum Ring': '28', 'Final Form': '29', 'Anti-Form': '30', 'Master Form': '31', 'Torn Pages': '32', "Master's Ring": '34', 'Moon Amulet': '35', 'Star Charm': '36', 'Skill Ring': '38', 'Skillful Ring': '39', 'Soldier Earring': '40', 'Kingdom Key': '41', 'Oathkeeper': '42', 'Oblivion': '43', 'Detection Saber': '44', 'Edge of Ultima': '45', 'Fencer Earring': '46', 'Mage Earring': '47', 'Slayer Earring': '48', "Knight's Shield": '49', 'Detection Shield': '50', 'Test The King (Shield)': '51', 'Cosmic Ring': '52', 'Medal': '53', 'Battlefields of War': '54', 'Sword of Ancestors': '55', 'Cosmic Arts': '56', 'Shadow Archive': '57', 'Shadow Archive+': '58', "Beast's Claw": '59', 'Bone Fist': '60', 'Proud Fang': '61', 'Skill and Crossbones': '62', 'Lucky Ring': '63', 'Full Bloom': '64', 'Draw Ring': '65', 'Full Bloom+': '66', 'Elven Bandanna': '67', 'Divine Bandanna': '68', 'Power Band': '69', 'Buster Band': '70', 'Anti-Form Dummy': '71', 'Scimitar': '72', 'Way of Dawn': '73', 'Identity Disk': '74', "Mage's Staff": '75', 'Protect Belt': '78', 'Gaia Belt': '79', 'FAKE (looks like Sword of the Ancestors)': '80', 'FAKE (Keyblade,looks like Kingdom Key)': '81', 'Guard': '82', 'Magnet Element': '87', 'Reflect Element': '88', 'Navigational Map (Map for Debug Mode?)': '89', 'Castle Map': '90', 'Basement Map': '91', 'Castle Walls Map': '92', 'High Jump LV1': '94', 'High Jump LV2': '95', 'High Jump LV3': '96', 'High Jump MAX': '97', 'Quick Run LV1': '98', 'Quick Run LV2': '99', 'Quick Run LV3': '100', 'Quick Run MAX': '101', 'Aerial Dodge LV1': '102', 'Aerial Dodge LV2': '103', 'Aerial Dodge LV3': '104', 'Aerial Dodge MAX': '105', 'Glide LV1': '106', 'Glide LV2': '107', 'Glide LV3': '108', 'Glide MAX': '109', 'Cosmic Belt': '111', 'Encampment Area Map': '112', 'Village Area Map': '113', 'Cornerstone Hill Map': '114', 'Window of Time Map (I)': '115', 'Lilliput Map': '116', 'Building Site Map': '117', "Mickey's House Map": '118', 'Disney Castle Map': '119', 'Agrabah Map': '120', 'Cave of Wonders Map': '121', 'Ruins Map': '122', 'Undersea Kingdom Map': '123', 'Starry Hill Map': '124', '100 Acre Wood Map': '125', "Rabbit's Howse Map": '126', "Piglett's Howse Map": '127', "Kanga's Howse Map": '128', 'Spooky Cave Map': '129', 'Palace Map': '130', 'Tent': '131', 'Shock Charm': '132', 'Shock Charm+': '133', 'Coliseum Map': '134', 'Underworld Map': '135', 'Caverns Map': '136', 'Upper Slash': '137', 'Scan': '138', 'Adamant Shield': '139', 'Chain Shield': '140', 'Ogre Shield': '141', 'Falling Star': '142', 'Dream Cloud': '143', 'Knight Defender': '144', 'Genji Shield': '145', 'Akashic Record': '146', 'Nobody Guard': '147', 'Hammer Staff': '148', 'Victory Bell': '149', 'Meteor Staff': '150', 'Comet Staff': '151', "Lord's Broom": '152', 'Wisdom Wand': '153', 'Rising Dragon': '154', 'Nobody Lance': '155', "Shaman's Relic": '156', 'Grand Ribbon': '157', 'Aerial Recovery': '158', 'Lamp Charm (Summon Genie)': '159', 'Feather Charm (Summon Peter Pan)': '160', 'Staff of Detection (Detects Movement?)': '161', 'Combo Plus': '162', 'Air Combo Plus': '163', 'Donald Fire': '165', 'Donald Blizzard': '166', 'Donald Thunder': '167', 'Donald Cure': '168', 'Fire Bangle': '173', 'Fira Bangle': '174', 'Healing Water': '176', 'Furious Shout': '177', 'Cure Potion': '187', 'Healing Herb': '190', 'Slow 3': '195', 'Firaga Bangle': '197', 'Trinity Limit': '198', 'Fantasia': '199', 'Flare Force': '200', 'Tornado Fusion': '201', 'Teamwork': '202', 'Trick Fantasy': '203', 'Overdrive': '204', 'Howling Moon': '205', 'Applause, Applause': '206', 'Dragonblase': '207', 'Eternal Session': '208', "King's Pride": '209', 'Treasure Isle': '210', 'Complete Compilement': '211', 'Pulsing Thunder': '215', 'Brave Shot': '216', 'Brave Beat': '217', 'Sonic Strike': '218', 'Sonic End': '219', 'Wisdom Shot': '220', 'Mobile Action': '221', 'Synch Blade': '223', 'Magic Haste': '224', 'Magic Spice': '225', "Secret Ansem's Report 1": '226', "Secret Ansem's Report 2": '227', "Secret Ansem's Report 3": '228', "Secret Ansem's Report 4": '229', "Secret Ansem's Report 5": '230', "Secret Ansem's Report 6": '231', "Secret Ansem's Report 7": '232', "Secret Ansem's Report 8": '233', "Secret Ansem's Report 9": '234', "Secret Ansem's Report 10": '235', "Secret Ansem's Report 11": '236', "Secret Ansem's Report 12": '237', "Secret Ansem's Report 13": '238', 'Over the Horizon': '246', 'Omega Finale': '247', 'Reflect Dummy': '248', 'Upper Dummy': '249', 'Halloween Town Map': '250', 'Naval Map': '251', 'Pride Rock Map': '252', 'Marketplace Map': '253', 'Pit Cell Area Map': '254', 'Twilight Town Map': '255', 'Dark City Map': '256', 'Master Strike': '257', 'Disaster': '258', 'Endless Magic': '259', 'Master Magic': '261', 'Slapshot': '262', 'Dodge Slash': '263', 'Slide Dash': '264', 'Guard Break': '265', 'Explosion': '266', 'Finishing Leap': '267', 'Counterguard': '268', 'Aerial Sweep': '269', 'Aerial Spiral': '270', 'Horizontal Slash': '271', 'Aerial Finish': '272', 'Retaliating Slash': '273', 'Drive Recovery': '274', 'High Drive Recovery': '275', 'Power Boost': '276', 'Magic Boost': '277', 'Defense Boost': '278', 'AP Boost': '279', 'Dark Shard': '280', 'Dark Stone': '281', 'Dark Gem': '282', 'Dark Crystal': '283', 'Firagun Bangle': '284', 'Blizzard Armlet': '286', 'Blizzara Armlet': '287', 'Blizzaga Armlet': '288', 'Blizzagun Armlet': '289', 'Thunder Trinket': '291', 'Thundara Trinket': '292', 'Thundaga Trinket': '293', 'Thundagun Trinket': '294', 'Shadow Anklet': '296', 'Dark Anklet': '297', 'Midnight Anklet': '298', 'Chaos Anklet': '299', 'Abas Chain': '301', 'Aegis Chain': '302', 'Acrisius': '303', 'Ribbon': '304', 'Champion Belt': '305', 'Petit Ribbon': '306', 'Acrisius+': '307', 'Cosmic Chain': '308', 'Blazing Shard': '317', 'Blazing Stone': '318', 'Blazing Gem': '319', 'Blazing Crystal': '320', 'Lightning Shard': '325', 'Lightning Stone': '326', 'Lightning Gem': '327', 'Lightning Crystal': '328', 'Power Shard': '329', 'Power Stone': '330', 'Power Gem': '331', 'Power Crystal': '332', 'Lucid Shard': '333', 'Lucid Stone': '334', 'Lucid Gem': '335', 'Lucid Crystal': '336', 'Dense Shard': '337', 'Dense Stone': '338', 'Dense Gem': '339', 'Dense Crystal': '340', 'Twilight Shard': '341', 'Twilight Stone': '342', 'Twilight Gem': '343', 'Twilight Crystal': '344', 'Mythril Shard': '345', 'Mythril Stone': '346', 'Mythril Gem': '347', 'Mythril Crystal': '348', 'Bright Shard': '349', 'Bright Stone': '350', 'Bright Gem': '351', 'Bright Crystal': '352', 'Energy Shard': '353', 'Energy Stone': '354', 'Energy Gem': '355', 'Energy Crystal': '356', 'Serenity Shard': '357', 'Serenity Stone': '358', 'Serenity Gem': '359', 'Serenity Crystal': '360', 'Orichalcum+': '361', 'Munny Pouch (From Olette)': '362', 'Crystal Orb': '363', "Seifer's Trophy": '364', 'Tournament Poster': '365', 'Poster': '366', 'Letter': '367', "Namine's Sketches": '368', 'Membership Card': '369', 'Olympus Stone': '370', "Auron's Statue": '371', 'Cursed Medallion': '372', 'Present': '373', 'Decoy Presents': '374', 'Ice Cream': '375', 'Picture': '376', 'Orichalcum': '377', 'Frost Shard': '378', 'Frost Stone': '379', 'Frost Gem': '380', 'Frost Crystal': '381', 'Mega Recipe': '382', 'Baseball Charm (Summon Chicken Little)': '383', 'Struggle Sword': '384', 'Auto Valor': '385', 'Auto Wisdom': '386', 'Auto Master': '387', 'Auto Final': '388', 'Auto Summon': '389', 'Combo Boost': '390', 'Air Combo Boost': '391', 'Reaction Boost': '392', 'Finishing Plus': '393', 'Negative Combo': '394', 'Berserk Charge': '395', 'Damage Drive': '396', 'Drive Boost': '397', 'Form Boost': '398', 'Summon Boost': '399', 'Combination Boost': '400', 'Experience Boost': '401', 'Leaf Bracer': '402', 'Magic Lock-On': '403', 'No Experience': '404', 'Draw': '405', 'Jackpot': '406', 'Lucky Lucky': '407', 'Fire Boost': '408', 'Blizzard Boost': '409', 'Thunder Boost': '410', 'Item Boost': '411', 'MP Rage': '412', 'MP Haste': '413', 'Defender': '414', 'Second Chance': '415', 'Once More': '416', 'Auto Limit (I)': '417', 'Auto Change': '418', 'Hyper Healing': '419', 'Auto Healing': '420', 'MP Hastera': '421', 'MP Hastega': '422', 'Goofy Tornado': '423', 'Goofy Turbo': '425', 'Slash Frenzy': '426', 'Quickplay': '427', 'Divider': '428', 'Goofy Bash': '429', 'Ferocious Rush': '430', 'Blazing Fury': '431', 'Icy Terror': '432', 'Bolts of Sorrow': '433', 'Mushu Fire': '434', 'Flametongue': '435', 'Dark Shield': '436', 'Dark Aura': '438', 'Fierce Claw': '439', 'Groundshaker': '440', 'Scouting Disk': '444', 'Slow 2': '445', 'No Mercy': '446', 'Rain Storm': '447', 'Bone Smash': '448', 'Star Recipe': '449', 'Recovery Recipe': '450', 'Skill Recipe': '451', 'Guard Recipe': '452', 'Dummy 06': '453', 'Dummy 07': '454', 'Dummy 08': '455', 'Dummy 09': '456', 'Dummy 10': '457', 'Dummy 11': '458', 'Dummy 12': '459', 'Dummy 13': '460', 'Dummy 14': '461', 'Dummy 15': '462', 'Dummy 16': '463', 'Road to Discovery': '464', 'Strength Beyond Strength': '465', 'Book of Shadows': '466', 'Cloaked Thunder': '467', 'Eternal Blossom': '468', 'Rare Document': '469', 'Dummy 23': '470', 'Dummy 24': '471', 'Dummy 25': '472', 'Dummy 26': '473', 'Dummy 27': '474', 'Style Recipe': '475', 'Moon Recipe': '476', 'Queen Recipe': '477', 'King Recipe': '478', 'Ultimate Recipe': '479', 'Star Seeker': '480', 'Hidden Dragon': '481', 'Save the Queen': '482', 'Save The King': '483', "Hero's Crest": '484', 'Monochrome': '485', 'Follow the Wind': '486', 'Circle of Life': '487', 'Photon Debugger': '488', 'Gull Wing': '489', 'Rumbling Rose': '490', 'Guardian Soul': '491', 'Wishing Lamp': '492', 'Decisive Pumpkin': '493', 'Sleeping Lion': '494', 'Sweet Memories': '495', 'Mysterious Abyss': '496', 'Fatal Crest': '497', 'Bond of Flame': '498', 'Fenrir': '499', 'Ultima Weapon': '500', 'Struggle Wand': '501', 'Struggle Hammer': '502', 'Save the Queen+': '503', 'Save the King+': '504', 'The Interceptor Map': '505', 'The Black Pearl Map': '506', 'Isla De Muerta Map': '507', 'Ship Graveyard Map': '508', 'Christmas Town Map': '509', 'Curly Hill Map': '510', 'Oasis Map': '511', 'Savannah Map': '512', 'Castle Perimeter Map': '513', 'The Great Maw Map': '514', 'I/O Tower Map': '515', 'Central Computer Core Map': '516', 'Solar Sailer Simulation Map': '517', 'Window of Time Map (II)': '518', 'Auto Assault': '519', 'Finishing Blast': '520', 'Combo Upper': '521', 'Aerial Impulse': '522', 'Retaliating Smash': '523', 'Promise Charm': '524', 'Running Tackle': '525', 'Dash': '526', 'Final Arcana': '527', 'Final Strike': '528', 'Final Arts': '529', 'Crime & Punishment': '530', 'Sunset Hill Map': '531', 'Mansion Map': '532', 'Tower Map': '533', 'DH Map': '534', 'Munny Pouch (From Mickey)': '535', 'Castle That Never Was Map': '536', 'Hades Cup Trophy': '537', 'The Struggle Trophy': '538', 'Combo Master': '539', 'Drive Converter': '540', 'Light & Darkness': '541', 'Damage Control': '542', 'Two Become One': '543', "Winner's Proof": '544', 'Centurion': '545', 'Centurion+': '546', 'Plain Mushroom': '547', 'Plain Mushroom+': '548', 'Precious Mushroom': '549', 'Precious Mushroom+': '550', 'Premium Mushroom': '551', 'Frozen Pride': '552', 'Frozen Pride+': '553', 'Joyous Mushroom': '554', 'Joyous Mushroom+': '555', 'Majestic Mushroom': '556', 'Majestic Mushroom+': '557', 'Ultimate Mushroom': '558', 'Flash Step': '559', 'Aerial Dive': '560', 'Magnet Burst': '561', 'Vicinity Break': '562', 'Limit Form': '563', 'Dodge Roll LV1': '564', 'Dodge Roll LV2': '565', 'Dodge Roll LV3': '566', 'Dodge Roll MAX': '567', 'Auto Limit (II)': '568', 'Sonic Rave': '569', 'Last Arcanum': '570', 'Strike Raid': '571', 'Infinity': '572', 'Zantetsuken': '573', 'Ripple Drive': '574', 'Hurricane Period': '575', 'Remembrance Shard': '576', 'Remembrance Stone': '577', 'Remembrance Gem': '578', 'Remembrance Crystal': '579', 'Tranquility Shard': '580', 'Tranquility Stone': '581', 'Tranquility Gem': '582', 'Tranquility Crystal': '583', 'Lost Illusion': '584', 'Manifest Illusion': '585', 'Dark Remembrance Map': '586', 'Zantetsu Counter': '587', 'Reflect Combo': '588', 'HP Gain': '589', 'Depths of Remembrance Map': '590', 'Garden of Assemblage Map': '592', 'Proof of Connection': '593', 'Proof of Nonexistence': '594', 'Proof of Peace': '595', 'Protect': '596', 'Protectra': '597', 'Protectga': '598', "Executive's Ring": '599', "Shaman's Relic+": '600', 'Akashic Record+': '601'}

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
        "Demyx OC",
        "Final Xemnas",
        "Grim Reaper I",
        "Grim Reaper II",
        "Groundshaker",
        "Hades Intro",
        "Hades Escape",
        "Hades II",
        "Hayner",
        "Hostile Program",
        "Hydra",
        "Jafar",
        "Larxene",
        "Luxord",
        "Marluxia",
        "MCP",
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
        "Seifer",
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
        "Zexion"
    ]
}
class bossrush:
    def __init__(self, game, options, seed=None):
        if game not in supported_games:
            raise Exception("Game not supported")
        self.game = game
        self.options = options
        if not seed:
            self.seed = int(time.time())

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
        "route": False,
        "abilities_start_equipped": True,
        "randomize_starting_stuff": False,
        "platform": "pc",
        "open_menu_before_each_fight": False,
        "seed": ""
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



    kh2 = KingdomHearts2()
    source_bosses = kh2.get_valid_bosses()
    bosses = [b for b in source_bosses if b not in IGNORE_BOSSES]
    options.add_argument("-boss_in_room", choices=["vanilla", "random"] + bosses, default=last_settings.get("boss_in_room"))
    options.add_argument("-starting_room", choices=["default"] + source_bosses, default=last_settings.get("starting_room"))
    options.add_argument("-num_bosses", choices=["random"] + [str(l) for l in range(1,len(bosses))], default=last_settings.get("num_bosses"))
    options.add_argument("-level", choices=["random"] + [str(l) for l in range(1,99)], default=last_settings.get("level"))
    options.add_argument("-route", choices=["random"] + list(ROUTES.keys()), default=last_settings.get("route"))
    options.add_argument("-randomize_starting_stuff", action="store_true", default=last_settings.get("randomize_starting_stuff"))
    options.add_argument("-abilities_start_equipped", action="store_true", default=last_settings.get("abilities_start_equipped"))
    options.add_argument("-open_menu_before_each_fight", action="store_true", default=last_settings.get("open_menu_before_each_fight"))
    options.add_argument("-platform", choices=["ps2", "pc"], default=last_settings.get("platform"))
    options.add_argument("-seed", default=last_settings.get("seed"))

    options.add_argument("-openkh_dir", help="Path to OpenKH folder.", default=default_config.get("openkh_dir"), widget='DirChooser')

    # Parse and print the results
    if cli_args:
        args = parser.parse_args(cli_args)
    else:
        args = parser.parse_args()

    settings_to_write = {
        "boss_in_room": args.boss_in_room,
        "starting_room": args.starting_room,
        "num_bosses": args.num_bosses,
        "level": args.level,
        "route": args.route,
        "abilities_start_equipped": args.abilities_start_equipped,
        "randomize_starting_stuff": args.randomize_starting_stuff,
        "open_menu_before_each_fight": args.open_menu_before_each_fight,
        "platform": args.platform,
        "seed": args.seed
    }
    config_to_write = {
        "openkh_dir": args.openkh_dir
    }
    json.dump(config_to_write, open("config.json", "w"))
    json.dump(settings_to_write, open("last_settings.json", "w"))

    seed_options = {
        "memory_expansion": True if args.platform == "pc" else False
    }
    if args.boss_in_room != "vanilla":
        if args.boss_in_room == "random":
            seed_options["boss"] = "One to One"
        else:
            seed_options["selected_boss"] = args.boss_in_room
    
    seed = args.seed or time.time()
    print("Using Seed {}".format(seed))
    random.seed(seed)
    

    num_bosses = int(args.num_bosses) if args.num_bosses != "random" else random.randint(1,len(bosses))
    starting_room = args.starting_room if args.starting_room != "random" else random.choice(bosses)
    level = int(args.level) if args.level != "random" else random.randint(1,99)
    route = args.route
    abilities_start_equipped = args.abilities_start_equipped
    randomize_starting_stuff = args.randomize_starting_stuff
    open_menu_before_each_fight = args.open_menu_before_each_fight
    openkh_dir = args.openkh_dir
    
    print(args.abilities_start_equipped)

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
        stuff = ["Scan","Guard Break", "Explosion",
        "Finishing Leap", "Guard",
        "Horizontal Slash", "Aerial Finish", "Berserk Charge"] + \
        ["Combo Boost" for _ in range(1)] + \
        ["Air Combo Boost" for _ in range(1)] + \
        ["Finishing Plus" for _ in range(2)] + \
        ["Negative Combo" for _ in range(1)] + \
        ["Second Chance", "Once More"] + \
        ["Fire Element" for _ in range(1)] + \
        ["Magnet Element" for _ in range(2)] + \
        ["Reflect Element" for _ in range(2)] + \
        ["Blizzard Element" for _ in range(1)] + \
        ["Valor Form", "Final Form", "Limit Form"] + \
        ["Decisive Pumpkin"] + \
        ["High Jump LV3", "Quick Run LV3", "Aerial Dodge LV3", "Glide LV3", "Dodge Roll LV3"] + \
        ["Wisdom Form", "Flash Step"]
        stuff = [ITEMS[s] for s in stuff]
        #TODO in my own testing I found 58 is the max number of items....
        if len(stuff) > 32:
            raise Exception("Error: Can't have more than 32 pieces of stuff")
        # Nonrandomized list is all magic at 'aga', all forms, scan, decisive pumpkin, second chance, once more, both negative combos, explosion, magnet splash, 2 combo and air combo boosts, finisher, magic lock on, 10 megaelixers,
    else:
        stuff = []
        MAXITEMS = 32
        for i in range(MAXITEMS):
            itemvalue = int(ITEMS[random.choice(ITEMS)])
            if abilities_start_equipped: # TODO This only works on randomize_starting_stuff and it would break non equipped stuff
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

    # TODO: don't pretend level doesn't exist

    assetgenerator.generatePlrp(hp=200, mp=100, ap=50, accessoryslt=3, armorslt=3, itemslt=3, items=stuff) #TODO implement

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
        if "msn" in b:
            return b["msn"][:2]
        # msn list is HE
        return "HE"
    def getroom(b):
        if "msn" in b:
            r = b["msn"][2:4]
            if r.lower() != "_c":
                return r
        return "09" # Assume colosseum
    world = getworld(first_boss)
    room = getroom(first_boss)
    program = first_boss["program"]
    # Have to lookup the world/rooms that the first boss is in
    asset = findRoomSource(modyml["assets"], "TT", "01")
    assetgenerator.generateEvt("TT", "01", 0x34, asset["source"], options={"jump_to":{"world":world, "room":room, "program":program}, "open_menu":True, "remove_event":True, "flags": ['0x84A'], "remove_excess_flags": True})

    boss_order.pop(0)

    for b in range(len(boss_order)): # changes to boss_order
        current_boss_name = bosses[b]
        current_boss = kh2.enemy_manager.enemy_records[current_boss_name]
        newworld = getworld(current_boss)
        newroom = getroom(current_boss)
        newprogram = current_boss["program"]
        asset = findRoomSource(modyml["assets"], world, room)
        print("Making evt for {}".format(current_boss_name))
        assetgenerator.generateEvt(world, room, "all", asset["source"], options={"remove_event": True, "jump_to":{"world": newworld, "room": newroom, "program": newprogram}, "open_menu":open_menu_before_each_fight, "remove_event":True})
        world = newworld
        room = newroom
        program = newprogram
    
    asset = findRoomSource(modyml["assets"], world, room)
    assetgenerator.generateEvt(world, room, "all", asset["source"], options={"remove_event": True, "jump_to":{"world": "ES", "room": "00", "program": 69}})

    yaml.dump(modyml, open(modyml_fn, "w"))

    print("All Done!")

if __name__ == "__main__":
    import sys
    main_ui()
    # if "cmd" in sys.argv:
    #     main()
    # else:
    #     main_ui()
