from khbr.KH2.AssetGenerator import AssetGenerator
from khbr.KH2.CutsceneRemover import CutsceneRemover
from khbr.KH2.ModWriter import ModWriter
from khbr.KH2.schemas.enemyseed import EnemySeed
from khbr.textutils import create_spoiler_text
from khbr.utils import print_debug
from khbr._config import DIAGNOSTICS
from khbr.randutils import pickbossmapping, pickenemymapping
from khbr.KH2.EnemyManager import EnemyManager
from khbr.KH2.LocationManager import LocationManager
from khbr.KH2.MissionManager import MissionManager
from khbr.KH2.SpawnManager import SpawnManager
from khbr.KH2.schemas.random_config import RandomConfig
import os, time
class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "02"
        self.spoilers = {"enemy": {}, "boss": {}}
        self.name = "kh2"
        self.memory_expansion = False
        self.datalocation = os.path.join(os.path.dirname(__file__), "data")
        self.enemy_manager = EnemyManager(self.datalocation)
        self.location_manager = LocationManager(self.datalocation)
        self.spawn_manager = SpawnManager()
        self.mission_manager = MissionManager(self.datalocation)

    def get_options(self):
        # Might want to define valid predicates at some point, as certain combinations can't be selected together
        return {
            "enemy": {"display_name": "Enemy Randomization Mode", "description": "Select if and how the enemies should be randomized. Available choices: One-to-One replacement ie all shadows become dusks. One-to-One per room: One-to-One but every room is rerandomized (so shadows in Parlor might be ice cubes, but in LOD Cave they might be fire cubes). Wild: every enemy entity in the game is completely randomized, but due to memory constraints no room can have more than 13 unique enemy types. If a selected enemy is filled in this setting is ignored and every enemy (almost) will become that enemy.",
                                    "type": "enemy", "possible_values": ["Disabled", "One to One", "One to One Per Room", "Wild"], "hidden_values": []},
            "selected_enemy": {"display_name": "Selected Enemy", "description": "Replaces every enemy with the selected enemy. Depending on the enemy may not generate a completable seed. This value is ignored if enemy randomization mode is not 'Selected Enemy'",
                                "type": "enemy", "possible_values": [None] + sorted(self.get_valid_enemies()), "hidden_values": []},
            "nightmare_enemies": {"display_name": "Nightmare Enemies", "description": "Replaces enemies using only the most difficult enemies in the game.",
                                "type": "enemy", "possible_values": [False, True], "hidden_values": []},
            "separate_nobodys": {"display_name": "Randomize Nobodys separately", "description": "Treats nobodys as a separate type of enemy, so they are only randomized among themselves.", 
                                 "type": "enemy", "possible_values": [False, True], "hidden_values": []},
            # TODO Need to write and validate this functionality with unit tests before releasing it
            "other_enemies": {"display_name": "Randomize misc enemies as Heartless", "description": "Enables and randomizes the following enemies as if they were heartless: Pirates, Bulky Vendors, Bees",
                                "type": "enemy", "possible_values": [False, True], "hidden_values": []},  
            "combine_enemy_sizes": {"display_name": "Combine Enemy Sizes (Unstable/PC Only)", "description": "Normally small enemies are randomized separately from big enemies to prevent crashing. On PC it is less likely to crash, so this option is to combine them (EXPERIMENTAL MAY CAUSE BAD CRASHES)",
                                 "type": "enemy", "possible_values": [False, True], "hidden_values": [], "experimental": True},
            "combine_melee_ranged": {"display_name": "Combine Melee and Ranged enemies (Unstable/PC Only)", "description": "Normally ranged and melee enemies are randomized separate from each other, both for difficulty and to reduce crashing. On PC it is less likely to crash, so this option will combine them (EXPERIMENTAL MAY CAUSE BAD CRASHES)",
                                 "type": "enemy", "possible_values": [False, True], "hidden_values": [], "experimental": True},

            "boss": {"display_name": "Boss Randomization Mode", "description": "Select if and how the bosses should be randomized. Available choices: One-to-One replacement just shuffles around where the bosses are located, but each boss is still present (some bosses may be excluded from the randomization). Wild will randomly pick an available boss for every location, meaning some bosses can be seen more than once, and some may never be seen. If a selected boss is filled in this setting is ignored and every boss (almost) will become that boss.",
                                "type": "boss", "possible_values": ["Disabled", "One to One", "Wild"], "hidden_values": []},
            "selected_boss": {"display_name": "Selected Boss", "description": "Replaces every boss possible with the selected boss. Depending on the boss may not generate a completable seed. This value is ignored if boss mode is not 'Selected Boss'",
                                "type": "boss", "possible_values": [None] + sorted(self.get_valid_bosses()), "hidden_values": []},
            "nightmare_bosses": {"display_name": "Nightmare Bosses", "description": "Replaces bosses using only the most difficult bosses in the game. Forces Boss Randomization Mode to be 'Wild'",
                                "type": "boss", "possible_values": [False, True], "hidden_values": []},
            "bosses_replace_enemies": {"display_name": "Bosses Can Replace Enemies (Unstable/PC only)", "description": "Replaces 0.5 percent of enemies in the game with a random boss. Should not put more than one boss as enemy in a single room, due to memory concerns. This option is intended for PC use only.",
                    "type": "boss", "possible_values": [False, True], "hidden_values": [], "experimental": True},
            "cups_bosses": {"display_name": "Randomize Cups Bosses", "description": "Include the coliseum bosses in the randomization pool'.",
                                "type": "boss", "possible_values": [True, False], "hidden_values": []},
            "data_bosses": {"display_name": "Randomize Data Bosses", "description": "Include the Data versions of organization members in the pool",
                                "type": "boss", "possible_values": [False, True], "hidden_values": []},      
            "gimmick_bosses": {"display_name": "Randomize Misc Bosses (Beta)", "description": "Include in the pool bosses that are mostly gimmicks or otherwise don't yet randomize cleanly (MCP, Jafar, Shadow Stalker, Groundshaker)",
                                "type": "boss", "possible_values": [False, True], "hidden_values": []},       
            "sephiroth": {"display_name": "Randomize Sephiroth", "description": "Include Sephiroth in the boss randomization pool",
                                "type": "boss", "possible_values": [False, True], "hidden_values": []},
            "terra": {"display_name": "Randomize Lingering Will", "description": "Include Lingering Will in the boss randomization pool",
                                "type": "boss", "possible_values": [False, True], "hidden_values": []},
            # "lua_bosses": {"display_name": "Advanced Boss Replacements (Must setup LuaBackend hook)", "description": "Takes advantage of Lua scripting and other methods to include bosses that are more difficult to randomize (ex: Final Xemnas). Generates a lua script that must be loaded via ModManager.",
            #                     "type": "boss", "possible_values": [False, True], "hidden_values": []},
            "mickey_rule": {"display_name": "Mickey Appearance Settings", "description": "Choose when Mickey appears. Options are 'follow', where mickey appears for the same bosses as in the vanilla game, regardless of their location. 'stay', where mickey appears in the same locations as in the vanilla game, regardless of the location. 'all', mickey will appear for every boss in the game, regardless of if mickey normally apepars there. 'none', mickey will never appear. Might make PS2 boss fights less stable",
                                "type": "boss", "possible_values": ["follow", "stay", "all", 'none'], "hidden_values": []},
            "scale_boss_stats": {"display_name": "Scale HP to Original Boss", "description": "Attempts to force bosses level/HP to the scale of the boss it is replacing. When turned off uses the games scaling which is partially based on the battle level of the world except for Datas/Terra which are always level 99.",
                                "type": "boss", "possible_values": [True, False], "hidden_values": []},
        }
    def get_hidden_options(self):
        # Options that are options but should not show up in the autogenerated UI in the generator
        return {
            "memory_expansion": {"display_name": "Use Expanded Memory", "description": "The PS2 version of the game has more limited enemy randomization capabilities. Turn this option on if playing on PC to remove these constraints.",
                                "possible_values": [False, True], "hidden_values": []},
            # utility mod options
            "remove_damage_cap": {"display_name": "Remove Damage Cap", "description": "Removes the damage cap for all enemies in the game.",
                                "possible_values": [], "hidden_values": [False, True]},
            "cups_give_xp": {"display_name": "Cups give XP", "description": "You will now gain XP and Form XP for killing enemies in the Olympus cups",
                                "possible_values": [], "hidden_values": [False, True]},
            "retry_data_final_xemnas": {"display_name": "Retry Data Final Xemnas", "description": "If you die to Data Final Xemnas, continue will put you right back into the fight, instead of having to fight Data Xemnas I again (warning will be a softlock if you are unable to beat Final Xemnas)",
                                "possible_values": [], "hidden_values": [False, True]},
            "retry_dark_thorn": {"display_name": "Retry Dark Thorn", "description": "If you die to Dark Thorn, continue will put you right back into the fight, instead of having to fight Shadow Stalker again (warning will be a softlock if you are unable to beat Shadow Stalker)",
                                "possible_values": [], "hidden_values": [False, True]},
            "remove_cutscenes": {"display_name": "Remove Cutscenes", "description": "Removes as many cutscenes from the game as possible. 3 different levels. 1 - Minimal: Remove as many cutscenes as possible without causing side effects. 2 - Non-Reward: Also remove cutscenes prior to forced fights, which causes the 'continue' on game over to work like 'retry' in later games (can be worked around easily with the auto-save mod). 3 - Maximum: Also remove cutscenes prior to receiving popup rewards, which causes the popops to not appear (although you still get the rewards, and they still show up on the tracker).",
                                "possible_values": [], "hidden_values": ["Disabled", "Minimal", "Non-Reward", "Maximum"]},
            "revenge_limit_rando": {"display_name": "Revenge Limit Randomizer", "description": "Randomizes the revenge value limit of each enemy/boss in the game. Can be either set to 0, set to basically infinity, randomly swapped, or set to a random value between 0 and 200",
                                "possible_values": [], "hidden_values": ["Vanilla", "Set 0", "Set Infinity", "Random Swap", "Random Values"]},
            "costume_rando": {"display_name": "Costume Randomizer (Beta)", "description": "Randomizes the different costumes that Sora/Donald/Goofy switch between in the different worlds (IE Space Paranoids could now be default sora, while anywhere default sora is used could be Christmas Town Sora",
                                "possible_values": [], "hidden_values": [False, True]},
            "party_member_rando": {"display_name": "Revenge Limit Randomizer (Beta)", "description": "Randomizes the World Character party member in each world.",
                                "possible_values": [], "hidden_values": [False, True]},

        }

    def get_valid_enemies(self):
        return self.enemy_manager.get_valid_enemies()
    def get_valid_bosses(self):
        return self.enemy_manager.get_valid_bosses()
        
    @staticmethod
    def get_utility_mods(options):
        utility_mods = []
        if options.get("remove_damage_cap"):
            utility_mods.append("remove_damage_cap")
        if options.get("cups_give_xp"):
            utility_mods.append("cups_give_xp")
        if options.get("retry_data_final_xemnas"):
            utility_mods.append("retry_data_final_xemnas")
        if options.get("retry_dark_thorn"):
            utility_mods.append("retry_dark_thorn")
        if options.get("costume_rando"):
            utility_mods.append("costume_rando")
        if options.get("party_member_rando"):
            utility_mods.append("party_member_rando")
        rmcs = options.get("remove_cutscenes", "Disabled")
        if rmcs and rmcs != "Disabled":
            utility_mods.append("remove_cutscenes{}".format(options.get("remove_cutscenes")))
        rvlr = options.get("revenge_limit_rando", "Vanilla")
        if rvlr and rvlr != "Vanilla":
            utility_mods.append("revenge_limit_rando{}".format(options.get("revenge_limit_rando")))
        return utility_mods

    def perform_randomization(self, options, seed=None):
        print_debug("Enemy Seed: {}".format(seed), override=False)
        if DIAGNOSTICS:
            start_time = time.time()
            print_debug("Starting Randomization: {}".format(options), override=True)

        enemymode = options.get("enemy", 'Disabled') if not options.get("selected_enemy") else options.get("selected_enemy")
        bossmode = options.get("boss", "Disabled") if not options.get("selected_boss") else options.get("selected_boss")
        nightmare_bosses = options.get("nightmare_bosses")
        memory_expansion = options.get("memory_expansion")
        if enemymode == "Wild" and not memory_expansion:
            raise Exception("Wild enemy mode only works on PC due to memory constraints on the PS2 version.")
        config = RandomConfig(
            memory_expansion = memory_expansion,
            utility_mods = self.get_utility_mods(options),
            scale_boss = options.get("scale_boss_stats", True),

            enemymode = enemymode,
            enemies = self.enemy_manager.get_enemies(options) if enemymode != 'Disabled' else {},
            combine_enemy_sizes = options.get("combine_enemy_sizes"),
            combine_melee_ranged = options.get("combine_melee_ranged"),
            separate_nobodys = options.get("separate_nobodys"),
            other_enemies = options.get("other_enemies"),
            nightmare_enemies = options.get("nightmare_enemies"),

            bossmode = bossmode,
            nightmare_bosses = nightmare_bosses,
            duplicate_bosses = nightmare_bosses or bossmode in ["Wild", "Selected Boss"],
            
            boss_as_enemy_overrides = self.enemy_manager.get_boss_as_enemy_list() if options.get("bosses_replace_enemies") else [],
            bosses = self.enemy_manager.get_boss_list(options) if bossmode != 'Disabled' else {},
            bosses_replace_enemies = options.get("bosses_replace_enemies"),

            mickey_rule = options.get("mickey_rule")
        )
        if options.get("selected_enemy"):
            config.selected_enemy = options["selected_enemy"]
        if options.get("selected_boss"):
            config.selected_boss = options["selected_boss"]

        rand_seed = EnemySeed(config=config)
        if bossmode or enemymode:
            self.create_seed(rand_seed)

        if config.utility_mods:
            if "cups_give_xp" in config.utility_mods:
                rand_seed.add_xp_for_cups()
                config.utility_mods.remove("cups_give_xp")
            rand_seed.utility_mods = config.utility_mods

        retry_dfx = "retry_data_final_xemnas" in config.utility_mods
        rand_seed.set_data_final_xemnas_retry(retry_dfx)
        if retry_dfx:
            config.utility_mods.remove("retry_data_final_xemnas")

        retry_dt = "retry_dark_thorn" in config.utility_mods
        rand_seed.set_dark_thorn_retry(retry_dt)
        if retry_dt:
            config.utility_mods.remove("retry_dark_thorn")

        party_rando = "party_member_rando" in config.utility_mods
        if party_rando:
            tron = {'ObjectId': 863, 'Serial': 13, 'index': 'new'}
            rand_seed.add_spawn("Space Paranoids", "Central Computer Core", "b_61", "69", "new", tron)
            if not "Final Xemnas" in rand_seed.ai_mods:
                rand_seed.ai_mods["Final Xemnas"] = "Final Xemnas"
                rand_seed.ai_mods["Final Xemnas (Data)"] = "Final Xemnas (Data)"

        rand_seed_json= rand_seed.toJson()
        if not rand_seed_json:
            raise Exception("Didn't randomize anything!")

        if seed:
            rand_seed_json["seed"] = seed

        if DIAGNOSTICS:
            end_time = time.time()
            print_debug("Enemy Randomization Complete: {}s".format(end_time-start_time))

        return rand_seed_json

    def create_seed(self, rand_seed: EnemySeed):
            rand_seed.bossmapping = pickbossmapping(self.enemy_manager.enemy_records, rand_seed.config.bosses) if not rand_seed.config.duplicate_bosses else None
            if rand_seed.config.enemies and rand_seed.config.enemymode != "Selected Enemy":
                categorized_enemies = self.enemy_manager.categorize_enemies(rand_seed.config.enemies, combine_sizes=rand_seed.config.combine_enemy_sizes, combine_ranged=rand_seed.config.combine_melee_ranged, separate_nobodys=rand_seed.config.separate_nobodys, other_enemies=rand_seed.config.other_enemies, ispc=rand_seed.config.memory_expansion)
                rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemy"], nightmare=rand_seed.config.nightmare_enemies)

                # Debug print out the enemy mapping
                for enemy in rand_seed.enemymapping:
                    print(enemy+"->"+rand_seed.enemymapping[enemy])
            
            self.location_manager.set_locations()
            spawns = self.location_manager.locations
            for w, world in spawns.items():
                for r, room in world.items():
                    self.location_manager.update_location(room, rand_seed.config)
                    rand_seed.wild_enemy_set = set()
                    if room.get("ignored"):
                        continue
                    if rand_seed.config.enemymode == "One to One Per Room":
                        rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemy"], nightmare=rand_seed.config.nightmare_enemies)

                    for sp, spawnpoint in room["spawnpoints"].items():
                        self.location_manager.update_location(spawnpoint, rand_seed.config)
                        if spawnpoint.get("ignored"):
                            continue
                        created_enemies = [] # This is a little weird it's just for location aimods, ideally they would be done at a different level than the spawnpoint level
                        bosses_as_enemies = 0
                        for i, entities in spawnpoint["sp_ids"].items(): # Fun fact: The internal game code refers to these as "unit"s I believe
                            # TODO might be able to make this just for entity in entities
                            for e in range(len(entities)):
                                entity = entities[e]
                                created_entity = {}
                                created_enemies.append(created_entity)

                                if rand_seed.config.bosses and entity["isboss"]:
                                    old_boss_object = self.enemy_manager.enemy_records[entity["name"]]
                                    old_boss_parent = self.enemy_manager.get_parent(entity["name"])
                                    if not self.spawn_manager.should_replace_boss(old_boss_object, old_boss_parent, rand_seed):
                                        continue

                                    new_boss = self.spawn_manager.get_new_boss(old_boss_object, old_boss_parent, rand_seed.config, rand_seed, self.enemy_manager.enemy_records)        
                                    if not new_boss:
                                        continue
                                    self.spoilers["boss"][entity["name"]] = new_boss

                                    # gotta get new boss object first because the data_replacements still needs to be set if it's a same replacement
                                    new_boss_object = self.enemy_manager.get_new_boss_object(old_boss_object, new_boss, rand_seed)
                                    # same replacement
                                    if new_boss == old_boss_object["name"]:
                                        # still need to update msn mapping for mickey rules
                                        rand_seed.update_msn_mapping(old_boss_object, old_boss_object)

                                        if old_boss_object["name"] == "Grim Reaper II":
                                            # hack to support both one gr2 placed in world and both. ideally the ai mod should just use a different number of medals based on being in gr2's room or not
                                            rand_seed.update_aimod(old_boss_object, new_boss_object)
                                        else:
                                            # When GR II replaces itself need to remove the medals that start on the ground
                                            continue

                                    rand_seed.add_spawn(w, r, sp, i, entity, new_boss_object)
                                    rand_seed.update_seed(old_boss_object, new_boss_object, w, r, sp, i)

                                elif rand_seed.config.enemies and not entity["isboss"]:
                                    old_enemy_object = self.enemy_manager.get_enemy_object_from_entity(entity)

                                    if not self.spawn_manager.should_replace_enemy(old_enemy_object):
                                        continue

                                    new_enemy = self.spawn_manager.get_new_enemy(rand_seed, old_enemy_object, room, existing_bosses_as_enemies=bosses_as_enemies)
                                    if not new_enemy:
                                        continue
                                    if new_enemy == old_enemy_object["name"] and not entity.get("nameForReplace", "") == new_enemy:
                                        continue

                                    new_enemy_object = self.enemy_manager.get_new_enemy_object(new_enemy, rand_seed)
                                    if new_enemy_object["type"] == "boss":
                                        bosses_as_enemies += 1
                                    created_entity.update(new_enemy_object)
                                    rand_seed.add_spawn(w, r, sp, i, entity, new_enemy_object)
                                    rand_seed.update_seed(old_enemy_object, new_enemy_object, w, r, sp, i)
            
                        for aimod in spawnpoint.get("aimods",[]):
                            createmod=True
                            for var in aimod["vars"]:
                                varvalue = aimod["vars"][var]
                                if varvalue.startswith("$"):
                                    varargs = varvalue[1:].split(".")
                                    if varargs[0] == "enemy":
                                        if len(created_enemies) == 0 and not aimod.get("boss_msn"):
                                            createmod=False
                                            continue # hack but these types of aimods should not be created when only boss rando is run
                                        index = int(varargs[1])
                                        argument = varargs[2]
                                        enemy = created_enemies[index]
                                        if not enemy:
                                            createmod=False
                                            continue # Likely means it's vanilla
                                        aimod["vars"][var] = enemy[argument]
                            
                            if createmod:
                                rand_seed.add_ai(aimod)
        
    def generate_files(self, outdir='', randomization={}, outzip=None):
        if DIAGNOSTICS:
            start_time = time.time()
            print_debug("Starting generation of files")

        if outzip:
            def _writeMethod(outfn, relfn, data):
                outzip.writestr(relfn, data)
            modwriter = ModWriter(outdir, _writeMethod)
        else:
            modwriter = ModWriter(outdir)

        assetgenerator = AssetGenerator(modwriter, spawn_manager=self.spawn_manager, location_manager=self.location_manager, enemy_manager=self.enemy_manager, ispc=randomization.get("memory_expansion", False))

        utility_mods = randomization.get("utility_mods", [])

        rvlrando = None
        for mod in utility_mods:
            if mod.startswith("revenge_limit_rando"):
                rvlrando = mod.replace("revenge_limit_rando", "")

        assetgenerator.generateObjEntry(randomization.get("object_map", {}))
        assetgenerator.generateEnmp(randomization.get("scale_map",{}), remove_damage_cap="remove_damage_cap" in utility_mods)
        rmcs = [u for u in utility_mods if u.startswith("remove_cutscenes")]
        if len(rmcs):
            cutsceneremover = CutsceneRemover(assetgenerator, mode=rmcs[0].replace("remove_cutscenes", ""))
            cutsceneremover.removeCutscenes()
        assetgenerator.generateAiMods(randomization.get("ai_mods"), rvlrando)
        assetgenerator.generateLuaMods(randomization.get("lua_mods"))
        assetgenerator.generateMsns(randomization.get("msn_map", {}), self.mission_manager.msninfo)
        # self.set_spawns() # TODO is this needed?
        self.location_manager.set_locations() # TODO this might be unneeded time waste????
        assetgenerator.generateSpawns(randomization.get("spawns", ""), randomization.get("subtract_map"))
        assetgenerator.generateCustomMoveset()
        assetgenerator.generateCustomCmd(randomization.get("cmd_mods", {}))
        randomize_party = "party_member_rando" in utility_mods
        randomize_costumes = "costume_rando" in utility_mods
        if randomize_party or randomize_costumes:
            assetgenerator.generateCustomMemt(randomize_party, randomize_costumes)

        if DIAGNOSTICS:
            end_time = time.time()
            print_debug("Files Generated: {}s".format(end_time-start_time))
        return assetgenerator.assets

    def generate_mod_basics(self, newname=None):
        return {"title": "KH2 Boss/Enemy Rando" if not newname else newname}
