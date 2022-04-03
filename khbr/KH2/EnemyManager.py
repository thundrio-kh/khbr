import json, os, yaml
from khbr._config import LIMITED_SIZE
from khbr.KH2.schemas.enemy_records import get_schema
class EnemyManager:
    def __init__(self, basepath):
        self.basepath = basepath
        self.enemy_records = None
        # TODO I think I'm loading json files a lot more than needed
        self.set_enemies()
        
    def get_valid_enemies(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "enemy"]
    def get_valid_bosses(self):
        return [b for b in self.enemy_records if self.enemy_records[b]["type"] == "boss"]
    def set_enemies(self, ispc=False):
        fn="full_enemy_records.json"
        if ispc:
            fn = "full_enemy_records_pc.json"
        with open(os.path.join(self.basepath, fn)) as f:
            self.enemy_records = json.load(f)
            
    def get_enemies(self):
        enemies = self.get_valid_enemies()
        enabled_enemies = [self.enemy_records[e] for e in enemies if self.enemy_records[e]["enabled"]]
        return enabled_enemies

    @staticmethod
    def add_tag(enemylist, tag):
        for enemy in enemylist:
            enemy["tags"].append(tag)
        return enemylist

    @staticmethod
    def remove_tag(enemylist, tag):
        for enemy in enemylist:
            enemy["tags"] = list(filter(lambda k: k != tag), enemylist)
        return enemylist

    def create_enemy_records(self, ispc=False, getavail=True):
        defaults = get_schema()
        with open(os.path.join(self.basepath, "enemies.yaml")) as f:
            enemies_f = yaml.load(f, Loader=yaml.FullLoader)
        enemies = {}
        parent_children_mapping = {}

        for name in enemies_f:
            main = enemies_f[name]
            for v in main["variations"]:
                variation = dict(main["variations"][v])
                variation["name"] = v
                self.inheritConfig(main, variation, defaults, ispc=ispc)
                variation["category"] = self.getCategory(variation, ispc=ispc)

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
                self.inheritConfig(enemies[parent], enemies[child], defaults, ispc=ispc)

        if getavail:
            # avail should only be filled in for parent bosses
            # I think this will work because of pass by reference
            bosses = {e: enemies[e] for e in enemies if enemies[e]["type"] == "boss" and enemies[e]["parent"] == enemies[e]["name"]}
            self.assign_availability(bosses, ispc)

        return enemies

    def lookup_object(self, name):
        return self.enemy_records[name]

    def get_parent(self, name):
        child = self.enemy_records.get(name)
        return self.enemy_records.get(child.get("parent"))

    def get_enemy_object_from_entity(self, entity):
        old_name = entity["nameForReplace"] if "nameForReplace" in entity else entity["name"]
        return self.enemy_records[old_name]

    def get_new_boss_object(self, old_boss_object, new_boss_name, rand_seed):
        new_boss_object = self.enemy_records[new_boss_name]
        # Due to how they use the same MSN in a lot of cases, org replacements should be the same between nobody + data versions
        if "organization" in old_boss_object["tags"]:
            new_parent = new_boss_object["parent"]
            old_parent = self.get_parent(old_boss_object["name"])
            rand_seed.data_replacements[old_parent["name"]] = new_parent
        if new_boss_object["replace_as"] and not rand_seed.config.selected_boss:
            new_boss_object = self.enemy_records[new_boss_object["replace_as"]]
        return new_boss_object

    def get_new_enemy_object(self, new_enemy_name, rand_seed):
        new_enemy_object = self.enemy_records[new_enemy_name]
        if new_enemy_object["replace_as"] and not rand_seed.config.selected_enemy:
            new_enemy_object = self.enemy_records[new_enemy_object["replace_as"]]
        return new_enemy_object

    @staticmethod
    def inheritConfig(parent, variation, defaults, ispc=False):
        # I don't know why this is sometimes called with parent == variation
        if parent == variation:
            return
        if ispc and "pc" in variation:
            for k in variation["pc"]:
                variation[k] = variation["pc"][k]
        keys_to_add = {} # keys in pc specific config not in overall
        for k in parent:
            if ispc and k == "pc":
                for k_pc in parent["pc"]:
                    value = parent["pc"][k_pc]
                    if k_pc not in parent:
                        keys_to_add[k_pc] = value
                    # Allow different blacklist/whitelists for pc vs ps2
                    elif type(value) == list:
                        for v in value:
                            if v not in parent[k_pc]:
                                parent[k_pc].append(v)
                    else:
                        parent[k_pc] = parent["pc"][k_pc]
            if k == "variations":
                if k not in variation: # confused, what is this for
                    variation[k] = list(parent[k].keys())
                continue
            if k not in variation:
                variation[k] = parent[k]
        parent.update(keys_to_add)
        for d in defaults:
            if d not in variation:
                variation[d] = defaults[d]
            else:
                if variation[d] == defaults[d] and d in parent:
                    if d not in ["children", "sizeTag"]:
                        variation[d] = parent[d]

    @staticmethod
    def getCategory(enemy, ispc=False):
        category = '-'.join(sorted(enemy["tags"]))
        if not ispc:
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

    def get_boss_list(self, options):
        nightmare_bosses = options.get("nightmare_bosses", False)
        ispc = options.get("memory_expansion", False)
        self.set_enemies(ispc)
        
        bosses = {}

        # Nightmare mode should override settings and always use datas and cups (until nightmare is a preset)
        # TODO On PC cups bosses are exhibiting crashy behavior, so just disable them always for now on PC
        use_cups_bosses = (not ispc) and (nightmare_bosses or options.get("cups_bosses"))
        use_data_bosses = nightmare_bosses or options.get("data_bosses")

        for k,v in self.enemy_records.items():
            if v["type"] != "boss":
                continue
            if not v["enabled"]:
                continue
            if nightmare_bosses and not v["isnightmare"]:
                continue
            if not use_cups_bosses and "cups" in v["tags"]:
                    continue
            if not use_data_bosses and "data" in v["tags"]:
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
                for child_name in boss["children"]:
                    child = self.enemy_records[child_name]
                    # This is involved in ommitting children that are excluded via tag
                    child["variations"] = [b for b in child["variations"] if b in bosses]

        return bosses

    @staticmethod
    def source_room_has_space(source_boss, dest_boss, ispc=False):
        if ispc:
            return True
        #print_debug("{} > {}: {} + {} >= {}".format(source_boss["name"], dest_boss["name"], source_boss["size"], dest_boss["room_size"], maxsize))
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
        if dest_boss["blacklist_destination"]:
            if source_boss["name"] in dest_boss["blacklist_destination"]:
                return True
        if dest_boss["whitelist_destination"]:
            if source_boss["name"] not in dest_boss["whitelist_destination"]:
                return True
        if source_boss["blacklist_source"]:
            if dest_boss["name"] in source_boss["blacklist_source"]:
                return True
        if source_boss["whitelist_source"]:
            if dest_boss["name"] not in source_boss["whitelist_source"]:
                return True
        if not source_boss["msn_replace_allowed"]:
            if dest_boss["msn_required"]:
                return True
        # Adding needsRC, RCblocked, needsTeleport, TeleportBlocked tags
        # if the dest boss has a behavior mod
        behavior_mods = {
            "needs_rc": "rc_blocked",
            "needs_teleport": "teleport_blocked"
        }
        dest_boss_behavior_mods = set(behavior_mods).intersection(dest_boss["tags"])
        for k in dest_boss_behavior_mods:
            if behavior_mods[k] in source_boss["tags"]:
                return True
        return False

    @staticmethod
    def _remove_category(category_string, category_to_remove):
        categories = category_string.split("-")
        if category_to_remove in categories:
            categories.remove(category_to_remove)
        return '-'.join(categories)


    def categorize_enemies(self, included_enemylist, combine_sizes=False, combine_ranged=False):
        if not self.enemy_records:
            self.set_enemies()
        categories = {}
        for e in included_enemylist:
            parent = self.enemy_records[e["parent"]]
            # Might not be respecting childrens tags properly
            category_name = parent["category"]
            if combine_sizes:
                category_name = self._remove_category(category_name, "large")
            if combine_ranged:
                category_name = self._remove_category(category_name, "ranged")
            if category_name not in categories:
                categories[category_name] = {}
            categories[category_name][parent["name"]] = parent
        return categories