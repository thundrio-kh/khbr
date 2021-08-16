from khbr.KH2.AssetGenerator import AssetGenerator
from khbr.KH2.ModWriter import ModWriter
from khbr.KH2.schemas.enemyseed import EnemySeed
from khbr.textutils import final_fight_text 
from khbr.utils import print_debug
from khbr._config import diagnostics
from khbr.randutils import pickbossmapping, pickenemymapping, pick_boss_to_replace, pick_enemy_to_replace
from EnemyManager import EnemyManager
from LocationManager import LocationManager
from MissionManager import MissionManager
from SpawnManager import SpawnManager
from schemas.random_config import RandomConfig
import os, time

#TODO data should be under kh2
class KingdomHearts2:
    def __init__(self):
        self.schemaversion = "02"
        self.spoilers = {"enemy": {}, "boss": {}}
        self.name = "kh2"
        self.unlimited_memory = False
        self.datalocation = os.path.join(os.path.dirname(__file__), "data", "kh2")
        self.enemy_manager = EnemyManager(self.datalocation)
        self.location_manager = LocationManager(self.datalocation)
        self.spawn_manager = SpawnManager()
        self.mission_manager = MissionManager(self.datalocation)

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
        if diagnostics:
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
            enemies = self.get_enemies() if enemymode != 'Disabled' else {},
            nightmare_enemies = options.get("nightmare_enemies"),

            bossmode = bossmode,
            nightmare_bosses = nightmare_bosses,
            duplicate_bosses = nightmare_bosses or bossmode in ["Wild", "Selected Boss"],
            bosses = self.get_boss_list(options) if bossmode != 'Disabled' else {}
        )
        if enemymode == "Selected Enemy":
            config.enemies = [options["selected_enemy"]]
        if bossmode == "Selected Boss":
            config.bosses = [options["selected_boss"]]

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

        if diagnostics:
            end_time = time.time()
            print_debug("Enemy Randomization Complete: {}s".format(end_time-start_time))

        return rand_seed_json

    def create_seed(self, config: RandomConfig, rand_seed: EnemySeed):
            rand_seed.bossmapping = pickbossmapping(self.enemy_manager.enemy_records, config.bosses) if not config.duplicate_bosses else None
            if config.enemies and config.enemymode != "Selected Enemy":
                categorized_enemies = self.enemy_manager.categorize_enemies(config.enemies)
                rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemies"], nightmare=config.nightmare_enemies)
            
            spawns = self.location_manager.get_locations()
            for w, world in spawns.items():
                for r, room in world.items():
                    self.location_manager.update_location(room, config)
                    if room.get("ignored"):
                        continue
                    if config.enemymode == "One to One Per Room":
                        rand_seed.enemymapping = pickenemymapping(self.enemy_manager.enemy_records, categorized_enemies, spoilers=self.spoilers["enemies"], nightmare=config.nightmare_enemies)
                    
                    for sp, spawnpoint in room["spawnpoints"].items():
                        self.location_manager.update_location(spawnpoint, config)
                        if spawnpoint.get("ignored"):
                            continue
                        for i, entities in spawnpoint["sp_ids"].items():
                            # TODO might be able to make this just for entity in entities
                            for e in range(len(entities)):
                                entity = entities[e]

                                if config.bosses and entity["isboss"]:
                                    old_boss_object = self.enemy_manager.enemy_records[entity["name"]]
                                    old_boss_parent = self.enemy_manager.get_parent(entity["name"])
                                    if not self.spawn_manager.should_replace_boss(old_boss_object, config, rand_seed):
                                        continue

                                    new_boss = self.spawn_manager.get_new_boss(old_boss_object, old_boss_parent, config, rand_seed)        
                                    if not new_boss:
                                        continue
                                    self.spoilers["boss"][entity["name"]] = new_boss
                                    # same replacement
                                    if not new_boss or new_boss == old_boss_object["name"]:
                                        continue

                                    new_boss_object = self.enemy_manager.get_new_boss_object(old_boss_object, new_boss, rand_seed)

                                    self.rand_seed.add_spawn(w, r, sp, i, entity, new_boss_object)
                                    #TODO spoilers should move into rand_seed
                                    self.rand_seed.update_seed(old_boss_object, new_boss_object)

                                elif config.enemies and not entity["isboss"]:
                                    old_enemy_object = self.get_enemy_object_from_entity(entity)

                                    if not self.spawn_manager.should_replace_enemy(old_enemy_object):
                                        continue

                                    new_enemy = self.spawn_manager.get_new_enemy(rand_seed, old_enemy_object)
                                    if not new_enemy or new_enemy == old_enemy_object["name"]:
                                        continue

                                    new_enemy_object = self.enemy_manager.get_new_enemy_object(new_enemy, rand_seed)
                                    self.rand_seed.add_spawn(w, r, sp, i, entity, new_enemy_object)
        
    def generate_files(self, outdir='', randomization={}, outzip=None):
        if diagnostics:
            start_time = time.time()
            print_debug("Starting generation of files")

        if outzip:
            def _writeMethod(outfn, relfn, data):
                outzip.writestr(relfn, data)
            modwriter = ModWriter(outdir, _writeMethod)
        else:
            modwriter = ModWriter(outdir)

        assetgenerator = AssetGenerator(assets, modwriter, spawn_manager=self.spawn_manager, location_manager=self.location_manager, enemy_manager=self.enemy_manager)

        utility_mods = randomization.get("utility_mods", [])

        assetgenerator.generateObjEntry(randomization.get("object_map", {}))
        assetgenerator.generateEnmp(randomization.get("scale_map",{}), remove_damage_cap="remove_damage_cap" in utility_mods)
        assetgenerator.generateAiMods(randomization.get("ai_mods"))
        assetgenerator.generateMsns(randomization.get("msn_map", {}, self.mission_manager.msninfo))
        self.set_spawns()
        assetgenerator.generateSpawns(self.spawns, randomization.get("spawns", ""), randomization.get("subtract_map"))
        
        if diagnostics:
            end_time = time.time()
            print_debug("Files Generated: {}s".format(end_time-start_time))
        return assetgenerator.assets

    def generate_mod_basics(self, newname=None):
        return {"title": "KH2 Boss/Enemy Rando" if not newname else newname}