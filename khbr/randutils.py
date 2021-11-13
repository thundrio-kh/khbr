import random

def pickbossmapping(enemy_records, parent_bossdict):
    while 1:
        bosslist = [b for b in parent_bossdict if parent_bossdict[b]["name"] == parent_bossdict[b]["parent"]]
        chosen = {}
        for k in sorted(bosslist, key=lambda k: len(parent_bossdict[k]["available"])):
            avail = [b for b in enemy_records[k]["available"] if not b in chosen.values()]
            if len(avail) == 0:
                break
            else:
                chosen_new_boss = random.choice(avail)
                chosen[k] = chosen_new_boss
        if len(bosslist) == len(chosen):
            return chosen

def pickenemymapping(enemy_records, categorized_enemies, spoilers=None, nightmare=None):
    # Create separate lists for each set of tags used by enemies
    mapping = {}
    for c in categorized_enemies:
        og = list(categorized_enemies[c].values()) # Remove duplicate parent entries
        new = list(og)
        if nightmare:
            new = [e for e in new if e["isnightmare"]]
        random.shuffle(new)
        for i in range(len(og)):
            old_parent = og[i]
            new_parent = new[i % len(new)]
            # So for each child of the new_parent, randomly pick a child of the old_parent
            # Then go through the variations of each, and add them to the mapping
            for old_child_name in old_parent["children"]:
                new_child_name = random.choice(new_parent["children"])
                new_child = enemy_records[new_child_name]
                old_child = enemy_records[old_child_name]
                for old_variation_name in old_child["variations"]:
                    new_variation_name = random.choice(list(new_child["variations"]))
                    mapping[old_variation_name] = new_variation_name
                    if spoilers is not None:
                        spoilers[old_variation_name] = new_variation_name

    return mapping
    #TODO unit test that len(enemylist) == len(list(mapping.keys()))
    
def pick_boss_to_replace(enemy_records, bossparentlist):
    enabled_parents = [b for b in bossparentlist if enemy_records[b]["enabled"]]
    if len(enabled_parents) == 0:
        raise Exception("No available parent bosses!")
    bossparent = enemy_records[random.choice(enabled_parents)]
    enabled_children = [b for b in bossparent["children"] if enemy_records[b]["enabled"]]
    if len(enabled_children) == 0:
        raise Exception("{} has no enabled children!".format(bossparent["name"]))
    bosschild = enemy_records[random.choice(enabled_children)]
    enabled_variations = [b for b in bosschild["variations"] if enemy_records[b]["enabled"]]
    if len(enabled_variations) == 0:
        raise Exception("{} has no enabled variations!".format(bosschild["name"]))
    chosen_boss = random.choice(enabled_variations)
    return chosen_boss

def pick_enemy_to_replace(old_enemy, enabled_enemies):
    options = [e["name"] for e in enabled_enemies if e["category"] == old_enemy["category"]]
    return random.choice(options)

def create_new_entity(old_entity, new_object):
    if old_entity == "new":
        entity = dict(new_object)
        entity["index"] = "new"
        return entity
    entity = dict(old_entity)
    entity["name"] = new_object["name"]
    return entity