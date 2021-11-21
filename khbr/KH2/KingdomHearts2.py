from khbr.KH2.AssetGenerator import AssetGenerator
from khbr.KH2.ModWriter import ModWriter
from khbr.KH2.schemas.enemyseed import EnemySeed
from khbr.textutils import create_spoiler_text
from khbr.utils import print_debug
from khbr._config import DIAGNOSTICS
from khbr.randutils import pickbossmapping, pickenemymapping
from KH2.EnemyManager import EnemyManager
from KH2.LocationManager import LocationManager
from KH2.MissionManager import MissionManager
from KH2.SpawnManager import SpawnManager
from KH2.schemas.random_config import RandomConfig
import os, time
class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "02"
        self.spoilers = {"enemy": {}, "boss": {}}
        self.name = "kh2"
        self.unlimited_memory = False
        self.datalocation = os.path.join(os.path.dirname(__file__), "data")
        self.enemy_manager = EnemyManager(self.datalocation)
        self.location_manager = LocationManager(self.datalocation)
        self.spawn_manager = SpawnManager()
        self.mission_manager = MissionManager(self.datalocation)

    def get_options(self):
        # Might want to define valid predicates at some point, as certain combinations can't be selected together
        return {
            "enemy": {"display_name": "Enemy Randomization Mode", "description": "Select if and how the enemies should be randomized. Available choices: One-to-One replacement ie all shadows become dusks. One-to-One per room: One-to-One but every room is rerandomized (so shadows in Parlor might be ice cubes, but in LOD Cave they might be fire cubes). Wild: every enemy entity in the game is completely randomized",
                                    "possible_values": ["Disabled", "One to One", "One to One Per Room", "Selected Enemy"], "hidden_values": ["Wild"]},
            "selected_enemy": {"display_name": "Selected Enemy", "description": "Replaces every enemy with the selected enemy. Depending on the enemy may not generate a completable seed. This value is ignored if enemy randomization mode is not 'Selected Enemy'",
                                "possible_values": [None] + sorted(self.get_valid_enemies()), "hidden_values": []},
            # "bosses_can_replace_enemies": {"display_name": "Bosses Can Replace Enemies", "description": "Replaces a small percentage of enemies in the game with a random boss. This option is intended for PC use only.",
            #                     "possible_values": [False, True], "hidden_values": []},
            "nightmare_enemies": {"display_name": "Nightmare Enemies", "description": "Replaces enemies using only the most difficult enemies in the game.",
                                "possible_values": [False, True], "hidden_values": []},
            # "separate_small_big_enemies": {"display_name": "Separate Small and Big Enemies", "description": "Randomizes big enemies among themselves and small enemies among themselves. Useful to prevent crashing"},
            #                     "possible_values": [True, False], "hidden_values": []},

            "memory_expansion": {"display_name": "Use Expanded Memory", "description": "The PS2 version of the game has more limited enemy randomization capabilities. Turn this option on if playing on PC to remove these constraints.",
                                "possible_values": [False, True], "hidden_values": []},

            "boss": {"display_name": "Boss Randomization Mode", "description": "Select if and how the bosses should be randomized. Available choices: One-to-One replacement just shuffles around where the bosses are located, but each boss is still present (some bosses may be excluded from the randomization). Wild will randomly pick an available boss for every location, meaning some bosses can be seen more than once, and some may never be seen. Selected Boss will replace every boss with a single selected boss.",
                                "possible_values": ["Disabled", "One to One", "Wild", "Selected Boss"], "hidden_values": []},
            "selected_boss": {"display_name": "Selected Boss", "description": "Replaces every boss possible with the selected boss. Depending on the boss may not generate a completable seed. This value is ignored if boss mode is not 'Selected Boss'",
                                "possible_values": [None] + sorted(self.get_valid_bosses()), "hidden_values": []},
            "nightmare_bosses": {"display_name": "Nightmare Bosses", "description": "Replaces bosses using only the most difficult bosses in the game. Forces Boss Randomization Mode to be 'Wild'",
                                "possible_values": [False, True], "hidden_values": []},
            "scale_boss_stats": {"display_name": "Scale Bosses", "description": "Attempts force bosses level/HP to the scale of the boss it is replacing. When turned off uses the games scaling which is partially based on the battle level of the world except for Datas/Terra which are always level 99.",
                                "possible_values": [True, False], "hidden_values": []},
            "cups_bosses": {"display_name": "Randomize Cups Bosses", "description": "Include the coliseum bosses in the randomization pool. In 'One for One'.",
                                "possible_values": [True, False], "hidden_values": []},
            "data_bosses": {"display_name": "Randomize Superbosses", "description": "Include the Data versions of organization members in the pool, as well as Terra and Sephiroth",
                                "possible_values": [False, True], "hidden_values": []},
        }
    def get_hidden_options(self):
        # Options that are options but should not show up in the autogenerated UI in the generator
        return {
            # utility mod options
            "remove_damage_cap": {"display_name": "Remove Damage Cap", "description": "Removes the damage cap for all enemies in the game.",
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
        return utility_mods

    def perform_randomization(self, options, seed=None):
        print_debug("Enemy Seed: {}".format(seed), override=False)
        if DIAGNOSTICS:
            start_time = time.time()
            print_debug("Starting Randomization: {}".format(options), override=True)

        enemymode = options.get("enemy", 'Disabled')
        bossmode = options.get("boss", "Disabled")
        nightmare_bosses = options.get("nightmare_bosses")
        config = RandomConfig(
            unlimited_memory = options.get("memory_expansion"),
            utility_mods = self.get_utility_mods(options),
            scale_boss = options.get("scale_boss_stats"),

            enemymode = enemymode,
            enemies = self.enemy_manager.get_enemies() if enemymode != 'Disabled' else {},
            nightmare_enemies = options.get("nightmare_enemies"),

            bossmode = bossmode,
            nightmare_bosses = nightmare_bosses,
            duplicate_bosses = nightmare_bosses or bossmode in ["Wild", "Selected Boss"],
            bosses = self.enemy_manager.get_boss_list(options) if bossmode != 'Disabled' else {}
        )
        if enemymode == "Selected Enemy":
            config.selected_enemy = options["selected_enemy"]
        if bossmode == "Selected Boss":
            config.selected_boss = options["selected_boss"]

        rand_seed = EnemySeed(config=config)
        if bossmode or enemymode:
            self.create_seed(rand_seed)

        if config.utility_mods:
            rand_seed.utility_mods = config.utility_mods

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
                categorized_enemies = self.enemy_manager.categorize_enemies(rand_seed.config.enemies)
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
                                    if not new_boss or new_boss == old_boss_object["name"]:
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