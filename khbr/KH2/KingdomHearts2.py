from khbr.KH2.AssetGenerator import AssetGenerator
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
            "enemy": {"display_name": "Enemy Randomization Mode", "description": "Select if and how the enemies should be randomized. Available choices: One-to-One replacement ie all shadows become dusks. One-to-One per room: One-to-One but every room is rerandomized (so shadows in Parlor might be ice cubes, but in LOD Cave they might be fire cubes). Wild: every enemy entity in the game is completely randomized (this is probably unstable and is only available for PC). If a selected enemy is filled in this setting is ignored and every enemy (almost) will become that enemy.",
                                    "type": "enemy", "possible_values": ["Disabled", "One to One", "One to One Per Room", "Wild"], "hidden_values": []},
            "selected_enemy": {"display_name": "Selected Enemy", "description": "Replaces every enemy with the selected enemy. Depending on the enemy may not generate a completable seed. This value is ignored if enemy randomization mode is not 'Selected Enemy'",
                                "type": "enemy", "possible_values": [None] + sorted(self.get_valid_enemies()), "hidden_values": []},
            "nightmare_enemies": {"display_name": "Nightmare Enemies", "description": "Replaces enemies using only the most difficult enemies in the game.",
                                "type": "enemy", "possible_values": [False, True], "hidden_values": []},
            "combine_enemy_sizes": {"display_name": "Combine Enemy Sizes (Experimental)", "description": "Normally small enemies are randomized separately from big enemies to prevent crashing. On PC it is less likely to crash, so this option is to combine them (EXPERIMENTAL MAY CAUSE BAD CRASHES)",
                                 "type": "enemy", "possible_values": [False, True], "hidden_values": [], "experimental": True},
            "combine_melee_ranged": {"display_name": "Combine Melee and Ranged enemies (Experimental)", "description": "Normally ranged and melee enemies are randomized separate from each other, both for difficulty and to reduce crashing. On PC it is less likely to crash, so this option will combine them (EXPERIMENTAL MAY CAUSE BAD CRASHES)",
                                 "type": "enemy", "possible_values": [False, True], "hidden_values": [], "experimental": True},


            "boss": {"display_name": "Boss Randomization Mode", "description": "Select if and how the bosses should be randomized. Available choices: One-to-One replacement just shuffles around where the bosses are located, but each boss is still present (some bosses may be excluded from the randomization). Wild will randomly pick an available boss for every location, meaning some bosses can be seen more than once, and some may never be seen. If a selected boss is filled in this setting is ignored and every boss (almost) will become that boss.",
                                "type": "boss", "possible_values": ["Disabled", "One to One", "Wild"], "hidden_values": []},
            "selected_boss": {"display_name": "Selected Boss", "description": "Replaces every boss possible with the selected boss. Depending on the boss may not generate a completable seed. This value is ignored if boss mode is not 'Selected Boss'",
                                "type": "boss", "possible_values": [None] + sorted(self.get_valid_bosses()), "hidden_values": []},
            "nightmare_bosses": {"display_name": "Nightmare Bosses", "description": "Replaces bosses using only the most difficult bosses in the game. Forces Boss Randomization Mode to be 'Wild'",
                                "type": "boss", "possible_values": [False, True], "hidden_values": []},
            "bosses_replace_enemies": {"display_name": "Bosses Can Replace Enemies (Experimental)", "description": "Replaces 0.5 percent of enemies in the game with a random boss. This option is intended for PC use only.",
                    "type": "boss", "possible_values": [False, True], "hidden_values": [], "experimental": True},
            "cups_bosses": {"display_name": "Randomize Cups Bosses", "description": "Include the coliseum bosses in the randomization pool. In 'One for One'.",
                                "type": "boss", "possible_values": [True, False], "hidden_values": []},
            "data_bosses": {"display_name": "Randomize Superbosses", "description": "Include the Data versions of organization members in the pool, as well as Terra and Sephiroth",
                                "type": "boss", "possible_values": [False, True], "hidden_values": []},
            "mickey_rule": {"display_name": "Mickey Appearance Settings", "description": "Choose when Mickey appears. Options are 'follow', where mickey appears for the same bosses as in the vanilla game, regardless of their location. 'stay', where mickey appears in the same locations as in the vanilla game, regardless of the location. 'all', mickey will appear for every boss in the game, regardless of if mickey normally apepars there. 'none', mickey will never appear. Might make PS2 boss fights less stable",
                                "type": "boss", "possible_values": ["follow", "stay", "all", 'none'], "hidden_values": []}
        }
    def get_hidden_options(self):
        # Options that are options but should not show up in the autogenerated UI in the generator
        return {
            "memory_expansion": {"display_name": "Use Expanded Memory", "description": "The PS2 version of the game has more limited enemy randomization capabilities. Turn this option on if playing on PC to remove these constraints.",
                                "possible_values": [False, True], "hidden_values": []},
            "scale_boss_stats": {"display_name": "Scale Bosses", "description": "Attempts force bosses level/HP to the scale of the boss it is replacing. When turned off uses the games scaling which is partially based on the battle level of the world except for Datas/Terra which are always level 99.",
                                "type": "boss", "possible_values": [True, False], "hidden_values": []},
            # utility mod options
            "remove_damage_cap": {"display_name": "Remove Damage Cap", "description": "Removes the damage cap for all enemies in the game.",
                                "possible_values": [], "hidden_values": [False, True]},
            "cups_give_xp": {"display_name": "Cups give XP", "description": "You will now gain XP and Form XP for killing enemies in the Olympus cups",
                                "possible_values": [], "hidden_values": [False, True]},
            "retry_data_final_xemnas": {"display_name": "Retry Data Final Xemnas", "description": "If you die to Data Final Xemnas, continue will put you right back into the fight, instead of having to fight Data Xemnas I again (warning will be a softlock if you are unable to beat Final Xemnas)",
                                "possible_values": [], "hidden_values": [False, True]}
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
        return utility_mods

    def perform_randomization(self, options, seed=None):
        print_debug("Enemy Seed: {}".format(seed), override=False)
        if DIAGNOSTICS:
            start_time = time.time()
            print_debug("Starting Randomization: {}".format(options), override=True)

        enemymode = options.get("enemy", 'Disabled') if not options.get("selected_enemy") else options.get("selected_enemy")
        bossmode = options.get("boss", "Disabled") if not options.get("selected_boss") else options.get("selected_boss")
        nightmare_bosses = options.get("nightmare_bosses")
        config = RandomConfig(
            memory_expansion = options.get("memory_expansion"),
            utility_mods = self.get_utility_mods(options),
            scale_boss = options.get("scale_boss_stats", True),

            enemymode = enemymode,
            enemies = self.enemy_manager.get_enemies() if enemymode != 'Disabled' else {},
            combine_enemy_sizes = options.get("combine_enemy_sizes"),
            combine_melee_ranged = options.get("combine_melee_ranged"),
            nightmare_enemies = options.get("nightmare_enemies"),

            bossmode = bossmode,
            nightmare_bosses = nightmare_bosses,
            duplicate_bosses = nightmare_bosses or bossmode in ["Wild", "Selected Boss"],
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

        print(rand_seed.msn_mapping)

        retry_dfx = "retry_data_final_xemnas" in config.utility_mods
        rand_seed.set_data_final_xemnas_retry(retry_dfx)
        if retry_dfx:
            config.utility_mods.remove("retry_data_final_xemnas")

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
                categorized_enemies = self.enemy_manager.categorize_enemies(rand_seed.config.enemies, combine_sizes=rand_seed.config.combine_enemy_sizes, combine_ranged=rand_seed.config.combine_melee_ranged)
                rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemy"], nightmare=rand_seed.config.nightmare_enemies)
            
            self.location_manager.set_locations()
            spawns = self.location_manager.locations
            for w, world in spawns.items():
                for r, room in world.items():
                    self.location_manager.update_location(room, rand_seed.config)
                    if room.get("ignored"):
                        continue
                    if rand_seed.config.enemymode == "One to One Per Room":
                        rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemy"], nightmare=rand_seed.config.nightmare_enemies)
                    
                    for sp, spawnpoint in room["spawnpoints"].items():
                        self.location_manager.update_location(spawnpoint, rand_seed.config)
                        if spawnpoint.get("ignored"):
                            continue
                        for i, entities in spawnpoint["sp_ids"].items():
                            # TODO might be able to make this just for entity in entities
                            for e in range(len(entities)):
                                entity = entities[e]

                                if rand_seed.config.bosses and entity["isboss"]:
                                    old_boss_object = self.enemy_manager.enemy_records[entity["name"]]
                                    old_boss_parent = self.enemy_manager.get_parent(entity["name"])
                                    if not self.spawn_manager.should_replace_boss(old_boss_object, old_boss_parent, rand_seed):
                                        continue

                                    new_boss = self.spawn_manager.get_new_boss(old_boss_object, old_boss_parent, rand_seed.config, rand_seed, self.enemy_manager.enemy_records)        
                                    if not new_boss:
                                        continue
                                    self.spoilers["boss"][entity["name"]] = new_boss
                                    # same replacement
                                    if new_boss == old_boss_object["name"]:
                                        # still need to update msn mapping for mickey rules
                                        rand_seed.update_msn_mapping(old_boss_object, old_boss_object)
                                        continue

                                    new_boss_object = self.enemy_manager.get_new_boss_object(old_boss_object, new_boss, rand_seed)

                                    rand_seed.add_spawn(w, r, sp, i, entity, new_boss_object)
                                    #TODO spoilers should move into rand_seed
                                    rand_seed.update_seed(old_boss_object, new_boss_object, w, r, sp, i)

                                elif rand_seed.config.enemies and not entity["isboss"]:
                                    old_enemy_object = self.enemy_manager.get_enemy_object_from_entity(entity)

                                    if not self.spawn_manager.should_replace_enemy(old_enemy_object):
                                        continue

                                    new_enemy = self.spawn_manager.get_new_enemy(rand_seed, old_enemy_object)
                                    if not new_enemy:
                                        continue
                                    if new_enemy == old_enemy_object["name"] and not entity.get("nameForReplace", "") == new_enemy:
                                        continue

                                    new_enemy_object = self.enemy_manager.get_new_enemy_object(new_enemy, rand_seed)
                                    rand_seed.add_spawn(w, r, sp, i, entity, new_enemy_object)
        
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

        assetgenerator.generateObjEntry(randomization.get("object_map", {}))
        assetgenerator.generateEnmp(randomization.get("scale_map",{}), remove_damage_cap="remove_damage_cap" in utility_mods)
        assetgenerator.generateAiMods(randomization.get("ai_mods"))
        assetgenerator.generateMsns(randomization.get("msn_map", {}), self.mission_manager.msninfo)
        # self.set_spawns() # TODO is this needed?
        self.location_manager.set_locations() # TODO this might be unneeded time waste????
        assetgenerator.generateSpawns(randomization.get("spawns", ""), randomization.get("subtract_map"))
        
        if DIAGNOSTICS:
            end_time = time.time()
            print_debug("Files Generated: {}s".format(end_time-start_time))
        return assetgenerator.assets

    def generate_mod_basics(self, newname=None):
        return {"title": "KH2 Boss/Enemy Rando" if not newname else newname}