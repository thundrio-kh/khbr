import json, os, yaml
from khbr._config import LIMITED_SIZE
from khbr.KH2.schemas.enemy_records import get_schema
from khbr.randutils import log_output
class EnemyManager:
    def __init__(self, basepath):
        self.basepath = basepath
        self.enemy_records = None
        # TODO I think I'm loading json files a lot more than needed
        self.set_enemies(True)
        
    def get_valid_enemies(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "enemy"]
    def get_valid_bosses(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "boss"]
    def set_enemies(self, moose=False, override={}):
        if not override:
            fn="full_enemy_records.json"
            if moose:
                fn = "full_enemy_records_moose.json"
            with open(os.path.join(self.basepath, fn)) as f:
                self.enemy_records = json.load(f)
        else:
            self.enemy_records = self.create_enemy_records(moose, override=override)

    def get_enemies(self, options):
        #TODO other enemies aren't being disabled properly
        enemies = self.get_valid_enemies()

        use_other_enemies = options.get("other_enemies")

        enabled_enemies = []
        for e in enemies:
            e_obj = self.enemy_records[e]

            if e_obj["enabled"]:
                if "other" in e_obj["tags"] and not use_other_enemies:
                    self.enemy_records[e]["enabled"] = False # they should stay vanilla when other is off
                    continue
            else:
                continue
            if "pirate" in e_obj["tags"] and not (use_other_enemies or "pirate" in str(options.get("selected_enemy", "")).lower()):
                e_obj["aimods"] = []
        
            enabled_enemies.append(e_obj)
        return enabled_enemies

    @staticmethod
    def add_tag(enemylist, tag):
        for enemy in enemylist:
            enemy["tags"].append(tag)
        return enemylist

    @staticmethod
    def remove_tag(enemylist, tag):
        for enemy in enemylist:
            enemy["tags"] = [t for t in enemy["tags"] if t != tag]
        return enemylist

    def merge_enemies_dicts(self, base, override):
        for k, v in override.items():
            if isinstance(v, dict):
                base[k] = self.merge_enemies_dicts(base.get(k, {}), v)
            else:
                base[k] = v
        return base

    def create_enemy_records(self, moose=False, getavail=True, override = {}):
        defaults = get_schema()
        with open(os.path.join(self.basepath, "enemies.yaml")) as f:
            enemies_f = yaml.load(f, Loader=yaml.FullLoader)
        # load overrides
        enemies_f = self.merge_enemies_dicts(enemies_f, override)

        enemies = {}
        parent_children_mapping = {}

        for name in enemies_f:
            main = enemies_f[name]
            for v in main["variations"]:
                variation = dict(main["variations"][v])
                variation["name"] = v
                self.inheritConfig(main, variation, defaults, moose=moose)

                variation["category"] = self.getCategory(variation, moose=moose)

                # TODO I'd like to make this better but I don't know how
                parent = variation["variationof"] or name
                if not variation["parent"]:
                    variation["parent"] = parent
                if parent not in parent_children_mapping:
                    parent_children_mapping[parent] = []
                parent_children_mapping[parent].append(name)
                enemies[v] = variation
        
        # This is making sure that children who aren't just variations also get inherited config
        # This should be in a separate loop to make sure the parents have been configured already
        for parent in parent_children_mapping:
            enemies[parent]["children"] = sorted(list(set(parent_children_mapping[parent])))
            for child in enemies[parent]["children"]:
                self.inheritConfig(enemies[parent], enemies[child], defaults, moose=moose)

        if getavail:
            # avail should only be filled in for parent bosses
            # I think this will work because of pass by reference
            bosses = {e: enemies[e] for e in enemies if enemies[e]["type"] == "boss" and enemies[e]["parent"] == enemies[e]["name"]}
            self.assign_availability(bosses, moose)

        return enemies

    def lookup_object(self, name):
        return self.enemy_records[name]
    
    def lookup_object_by_id(self, id):
        for name in self.enemy_records:
            if self.enemy_records[name]["obj_id"] == id:
                return self.enemy_records[name]
        return None

    def get_parent(self, name):
        child = self.enemy_records.get(name)
        return self.enemy_records.get(child.get("parent"))

    def get_enemy_object_from_entity(self, entity):
        old_name = entity["nameForReplace"] if "nameForReplace" in entity else entity["name"]
        return self.enemy_records[old_name]

    def get_new_boss_object(self, old_boss_object, new_boss_name, rand_seed):
        ardname = None
        # forced_variations won't work if the msn isn't in the old record
        if old_boss_object["msn"]:
            ardname = old_boss_object["msn"][:4]
        new_boss_object = self.enemy_records[new_boss_name]
        # Due to how they use the same MSN in a lot of cases, org replacements should be the same between nobody + data versions
        if "organization" in old_boss_object["tags"]:
            new_parent = new_boss_object["parent"]
            old_parent = self.get_parent(old_boss_object["name"])
            rand_seed.data_replacements[old_parent["name"]] = new_parent



        if new_boss_object["replace_as"] and not rand_seed.config.selected_boss:
            new_boss_object = self.enemy_records[new_boss_object["replace_as"]]
        for ard in new_boss_object["forced_variations"]:
            if ardname and ard == ardname:
                new_boss_object = self.enemy_records[new_boss_object["forced_variations"][ard]]
                log_output("Forcing specific variation")
        return new_boss_object

    def get_new_enemy_object(self, new_enemy_name, rand_seed):
        new_enemy_object = self.enemy_records[new_enemy_name]
        if new_enemy_object["replace_as"] and not rand_seed.config.selected_enemy:
            new_enemy_object = self.enemy_records[new_enemy_object["replace_as"]]
        return new_enemy_object

    @staticmethod
    def inheritConfig(parent, variation, defaults, moose=False):
        # I don't know why this is sometimes called with parent == variation
        if parent == variation:
            return
        if moose and "moose" in variation:
            for k in variation["moose"]:
                variation[k] = variation["moose"][k]
        keys_to_add = {} # keys in MOOSE specific config not in overall
        for k in parent:
            if moose and k == "moose":
                for k_moose in parent["moose"]:
                    value = parent["moose"][k_moose]
                    
                    if k_moose not in parent:
                        keys_to_add[k_moose] = value
                    # Allow different blacklist/whitelists for MOOSE vs ps2
                    elif type(value) == list:
                        for v in value:
                            if v not in parent[k_moose]:
                                parent[k_moose].append(v)
                    else:
                        parent[k_moose] = parent["moose"][k_moose]
        
        parent.update(keys_to_add)
        for k in parent:
            if k == "variations":
                if k not in variation: # confused, what is this for
                    variation[k] = list(parent[k].keys())
                continue
            if k not in variation:
                variation[k] = parent[k]
        
        # This must be adding the keys to a temporary version of the object, its not what gets written
        for d in defaults:
            if d not in variation:
                variation[d] = defaults[d]
            else:
                if variation[d] == defaults[d] and d in parent:
                    if d not in ["children", "sizeTag"]:
                        variation[d] = parent[d]

    @staticmethod
    def getCategory(enemy, moose=False):
        category = '-'.join(sorted(enemy["tags"]))
        if not moose:
            if enemy["sizeTag"]:
                category = "-".join([category, enemy["sizeTag"]])
        if len(category) > 0 and category[0] == "-":
            category = category[1:]
        return category

    def assign_availability(self, bosses, maxsize):
        for source_boss_name in bosses:
            source_boss = bosses[source_boss_name]
            avail = [] # These are bosses that are allowed to be here
            for dest_boss_name in bosses:
                dest_boss = bosses[dest_boss_name]
                if dest_boss_name == source_boss_name:
                    # Boss should always be allowed to be in it's own location
                    avail.append(dest_boss_name)
                    continue
                if self.isReplacementBlocked(source_boss, dest_boss):
                    continue
                if self.source_room_has_space(source_boss, dest_boss, maxsize):
                    avail.append(dest_boss_name)
            source_boss["available"] = avail

    def get_boss_as_enemy_list(self):
        l = []
        for _, v in self.enemy_records.items():
            if v["can_be_enemy_override"]:
                l.append(v["name"])
        return l

    def get_boss_list(self, options):
        nightmare_bosses = options.get("nightmare_bosses", False)
        moose = options.get("memory_expansion", False)
        
        bosses = {}

        # Nightmare mode should override settings and always use datas and cups (until nightmare is a preset)
        use_cups_bosses = nightmare_bosses or options.get("cups_bosses")
        use_data_bosses = nightmare_bosses or options.get("data_bosses")
        use_gimmick_bosses = options.get("gimmick_bosses")
        use_sephiroth = nightmare_bosses or options.get("sephiroth")
        use_terra = nightmare_bosses or options.get("terra")
        use_lua_bosses = options.get("lua_bosses")

        for k,v in self.enemy_records.items():
            if v["type"] != "boss":
                continue
            if not v["enabled"]:
                continue
            if nightmare_bosses and not v["isnightmare"]:
                continue
            if "cups" in v["tags"] and not use_cups_bosses:
                continue
            if "data" in v["tags"] and not use_data_bosses:
                continue
            if "terra" in v["tags"] and not use_terra:
                continue
            if "sephiroth" in v["tags"] and not use_sephiroth:
                continue
            if v.get("luamod") and not use_lua_bosses:
                continue
            bosses[k] = v
        
        # Need to adjust the children and variation and availablelists to not contain bosses which should be excluded
        # have to look at every source boss too so adjusting those sources, not just the ones that are available
        for boss_name in self.enemy_records:
            boss = self.enemy_records[boss_name]
            if boss["type"] != "boss":
                continue
            if boss["name"] == boss["parent"]:
                boss["children"] = [b for b in boss["children"] if b in bosses]
                boss["available"] = [b for b in boss["available"] if b in bosses]
                if use_gimmick_bosses:
                    boss["available"] += [b for b in boss["gimmick_source"] if b in bosses and b not in boss["available"]]
                for child_name in boss["children"]:
                    child = self.enemy_records[child_name]
                    # This is involved in ommitting children that are excluded via tag
                    child["variations"] = [b for b in child["variations"] if b in bosses]

        return bosses

    @staticmethod
    def source_room_has_space(source_boss, dest_boss, moose=False):
        if moose:
            return True
        #log_output(f"{source_boss['name']} > {dest_boss['name']}: {source_boss['size']} + {dest_boss['room_size']} >= {maxsize}")
        roommaxsize = source_boss["roommaxsize"] or LIMITED_SIZE
        availablespace = (roommaxsize - source_boss["room_size"]) * source_boss["roomsizemultiplier"]
        if availablespace - dest_boss["size"] < 0:
            return False
        return True

    @staticmethod
    def isReplacementBlocked(source_boss, dest_boss):
        # Is the replacement blocked by a manual setting inside the enemies.yaml?
        if not dest_boss["enabled"]:
            return True
        if not source_boss["source_replace_allowed"]:
            return True
        if source_boss["unchanged_file_size"] and (dest_boss["adds"] or dest_boss["subtracts"]):
            return True
        if source_boss["name"] in dest_boss.get("blacklist_destination", []):
            return True
        if dest_boss["whitelist_destination"]:
            if source_boss["name"] not in dest_boss["whitelist_destination"]:
                return True
        if dest_boss["name"] in source_boss.get("blacklist_source", [])+source_boss.get("gimmick_source", []):
            return True
        if source_boss["whitelist_source"]:
            if dest_boss["name"] not in source_boss["whitelist_source"]:
                return True
        if not source_boss["msn_replace_allowed"]:
            if dest_boss["msn_required"]:
                return True
        # Adding needsRC, RCblocked, needsTeleport, TeleportBlocked tags
        # if the dest boss has a behavior mod
        dest_behavior_mods = {
            "needs_rc": "rc_blocked",
            "needs_teleport": "teleport_blocked",
        }
        dest_boss_behavior_mods = set(dest_behavior_mods).intersection(dest_boss["tags"])

        for k in dest_boss_behavior_mods:
            if dest_behavior_mods[k] in source_boss["tags"]:
                return True
        # Sometimes the src boss has a behavior mod
        source_behavior_mods = {
            "needs_invuln": "cant_invuln"
        }
        source_boss_behavior_mods = set(source_behavior_mods).intersection(source_boss["tags"])
        for k in source_boss_behavior_mods:
            if source_behavior_mods[k] in dest_boss["tags"]:
                return True
        return False

    @staticmethod
    def _remove_category(category_string, category_to_remove):
        categories = category_string.split("-")
        if category_to_remove in categories:
            categories.remove(category_to_remove)
        return '-'.join(categories)


    def categorize_enemies(self, included_enemylist, combine_sizes=False, combine_ranged=False, separate_nobodys=True, other_enemies=False, moose=False):
        categories = {}
        for e in included_enemylist:
            parent = self.enemy_records[e["parent"]]
            # Might not be respecting childrens tags properly
            category_name = parent["category"]
            if not separate_nobodys:
                category_name = self._remove_category(category_name, "nobody")
            if combine_sizes:
                category_name = self._remove_category(category_name, "large")
            if combine_ranged:
                category_name = self._remove_category(category_name, "ranged")
            if other_enemies:
                category_name = self._remove_category(category_name, "other")
                category_name = self._remove_category(category_name, "pirate")
            if category_name not in categories:
                categories[category_name] = {}
            categories[category_name][parent["name"]] = parent
        return categories