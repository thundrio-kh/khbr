import unittest, os, functools, sys, traceback, pdb, yaml
from khbr.randomizer import Randomizer, KingdomHearts2
from khbr.KH2.ModWriter import ModWriter
from khbr.randutils import pickbossmapping
import testutils
import shutil


class Tests(unittest.TestCase):
    def test_valid_options(self):
        game = "kh2"
        options = {
            "selected_boss": "Zexion"
        }
        Randomizer()._validate_options(Randomizer()._get_game(game).get_options(), options)

    def test_tmpdir_create_delete(self):
        r = Randomizer(tempdir=testutils.get_tmp_path())
        fn, rmdir = r._make_tmpdir()
        assert os.path.isdir(fn)
        rmdir()
        assert not os.path.exists(fn)
    
    def test_read_all_zexion(self):
        seedfn = os.path.join(os.path.dirname(__file__), "KH2", "data", "testdata", "zexion.json")
        if os.path.exists(os.path.join(testutils.get_tmp_path(), "test")):
            shutil.rmtree(os.path.join(testutils.get_tmp_path(), "test"))
        rando = Randomizer(tempdir=testutils.get_tmp_path(), tempfn="test")
        b64 = rando.read_seed("kh2", seedfn=seedfn)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_all_xemnas(self):
        options = {"selected_boss": "Xemnas"}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_party_rando(self):
        options = {"party_member_rando": True}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_generate_one_one(self):
        options = {"boss": "One to One"}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_seedgen_boss_and_enemy_one_to_one(self):
        options = {"enemy": "One to One", "boss": "One to One"}
        randomization1 = testutils.generateSeed(options)
        randomization2 = testutils.generateSeed(options)
        randomization3 = testutils.generateSeed(options, seed="6789")
        assert randomization1 == randomization2
        assert randomization1 != randomization3
        testutils.validate_bosses_general(randomization1)
        testutils.validate_enemies_general(randomization1)

    def test_seedgen_enemy_one_to_one(self):
        options = {"enemy": "One to One"}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)

    def test_seedgen_enemy_one_to_one_other(self):
        options = {"enemy": "One to One", "other_enemies": False}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)

        for ai_mod in randomization["ai_mods"]:
            if ai_mod.startswith("B_CA040"):
                raise Exception("Undead Pirate C aimod should not be included")
        
        # validate no 'other' enemies are present
        kh2 = KingdomHearts2()
        for enemy in kh2.enemy_manager.enemy_records.values():
            if "other" in enemy["tags"]:
                assert not testutils.get_found(randomization, enemy["name"])

        options = {"enemy": "One to One", "other_enemies": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization)

        # validate 'other' enemies are present
        
        # Found an other
                # TODO ideally I would be testing that the old enemy was not an other/pirate enemy
        found_other = False
        for enemy in kh2.enemy_manager.enemy_records.values():
            if "other" in enemy["tags"]:
                if testutils.get_found(randomization, enemy["name"]):
                    found_other = True
        assert found_other

        found_undead_pirate = False
        for ai_mod in randomization["ai_mods"]:
            if ai_mod.startswith("B_CA040"):
                found_undead_pirate = True
        if not found_undead_pirate:
            raise Exception("Should have found Undead Pirate C aimod")


    def test_seedgen_enemy_one_to_one_pc(self):
        options = {"enemy": "One to One"}
        randomization = testutils.generateSeed(options)
        options["memory_expansion"] = True
        randomization_pc = testutils.generateSeed(options)
        testutils.validate_enemies_general(randomization_pc)
        assert randomization != randomization_pc 

    # def test_seedgen_enemy_one_to_one_nightmare(self):
    #     options = {"enemy": "One to One", "nightmare_enemies": True}
    #     randomization = testutils.generateSeed(options)
    #     testutils.validate_enemies_general(randomization)
    #     assert False == testutils.get_found(randomization, "Shadow")
        
    def test_seedgen_enemy_one_to_one_room(self):
        options = {"enemy": "One to One Per Room"}
        randomization = testutils.generateSeed(options)
        testutils.validate_enemies_general_perroom(randomization)

    # def test_seedgen_enemy_one_to_one_room_nightmare(self):
    #     options = {"enemy": "One to One Per Room", "nightmare_enemies": True}
    #     randomization = testutils.generateSeed(options)
    #     testutils.validate_enemies_general_perroom(randomization)
    #     assert False == testutils.get_found(randomization, "Shadow")

    def test_seedgen_enemy_selected(self):
        options = {"selected_enemy": "Shadow WI"}
        randomization = testutils.generateSeed(options)
        testutils.validate_selected(randomization, "Shadow WI", isboss=False)

    def test_seedgen_boss_selected(self):
        options = {"selected_boss": "Xemnas"}
        randomization = testutils.generateSeed(options)
        print("Selected Boss")
        testutils.validate_selected(randomization, "Xemnas", isboss=True)

    def test_seedgen_boss_mickey_rule(self):
        # Selected boss should be one that doesn't disallow mickey
        options = {"selected_boss": "Past Pete", "mickey_rule": "all"}
        randomization = testutils.generateSeed(options)
        assert randomization["msn_map"]["BB05_MS104B"]["setmickey"] == True # Dark Thorn
        assert randomization["msn_map"]["CA01_MS204"]["setmickey"] == True # GR 2
        assert randomization["msn_map"]["CA18_MS202"]["setmickey"] == True # GR 1
        assert randomization["msn_map"]["TT34_MS304"]["setmickey"] == False # Twilight Thorn, mickey is always off for Roxas
        options = {"selected_boss": "Past Pete", "mickey_rule": "none"}
        randomization = testutils.generateSeed(options)
        for key, value in randomization["msn_map"].items():
            assert value["setmickey"] == False
        options = {"selected_boss": "Past Pete", "mickey_rule": "stay"}
        randomization = testutils.generateSeed(options)
        assert randomization["msn_map"]["BB05_MS104B"]["setmickey"] == True # Dark Thorn
        assert randomization["msn_map"]["CA01_MS204"]["setmickey"] == False # GR 2
        assert randomization["msn_map"]["CA18_MS202"]["setmickey"] == True # GR 1
        options = {"selected_boss": "Past Pete", "mickey_rule": "follow"}
        randomization = testutils.generateSeed(options)
        # Technically should still test if the old locations get mickey disabled properly
        # But it requires knowing if the boss thats there would have mickey or not
        for old, new_object in randomization["msn_map"].items():
            if new_object["name"] == "BB05_MS104B":
                assert new_object["setmickey"] == True
            if new_object["name"] == "CA01_MS204":
                assert new_object["setmickey"] == False
            if new_object["name"] == "CA18_MS202":
                assert new_object["setmickey"] == True   

    def test_seedgen_boss_one_to_one(self):
        options = {"boss": "One to One"}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        testutils.validate_bosses_onetoone(randomization)
        assert False == testutils.get_found(randomization, tags=["data", "cups"])

    def test_seedgen_boss_one_to_one_pc(self):
        options = {"boss": "One to One"}
        randomization = testutils.generateSeed(options)
        options["memory_expansion"] = True
        randomization_pc = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization_pc, pc=True)
        testutils.validate_bosses_onetoone(randomization_pc, pc=True)
        assert False == testutils.get_found(randomization_pc, tags=["data", "cups"])
        assert randomization_pc != randomization

    def test_seedgen_boss_one_to_one_scaled(self):
        options = {"boss": "One to One", "scale_boss_stats": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        testutils.validate_scale_map(randomization)

    def test_seedgen_boss_one_to_one_cups(self):
        options = {"boss": "One to One", "cups_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        

    def test_seedgen_boss_one_to_one_datas(self):
        options = {"boss": "One to One", "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_one_to_one_cups_datas(self):
        options = {"boss": "One to One", "cups_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["data", "cups"])

    def test_seedgen_boss_wild(self):
        options = {"boss": "Wild"}
        randomization = testutils.generateSeed(options)
        print("Wild")
        print(randomization)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_randomized(randomization, "Final Xemnas")
        assert False == testutils.get_found(randomization, tags=["data", "cups"])

    def test_seedgen_boss_wild_cups(self):
        options = {"boss": "Wild", "cups_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        assert False == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_wild_datas(self):
        options = {"boss": "Wild", "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert False == testutils.get_found(randomization, tags=["cups"])
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_wild_cups_datas(self):
        options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_boss_wild_nightmare(self):
        options = {"boss": "Wild", "nightmare_bosses": True}
        randomization = testutils.generateSeed(options)
        print("Nightmare")
        print(randomization) 
        testutils.validate_bosses_general(randomization)
        assert True == testutils.get_found(randomization, tags=["cups"])
        assert True == testutils.get_found(randomization, tags=["data"])

    def test_seedgen_proderror1(self):
        options = {'boss': 'One to One', 'nightmare_bosses': False, 'selected_boss': None, 'enemy': 'One to One', 'selected_enemy': None, 'nightmare_enemies': False, 'scale_boss_stats': False, 'cups_bosses': False, 'data_bosses': False, 'memory_expansion': False}
        randomization = testutils.generateSeed(options)
        testutils.validate_bosses_general(randomization)

    def test_seedgen_error2(self):
        options = {'boss': 'One to One', 'nightmare_bosses': False, 'selected_boss': None, 'enemy': 'Disabled', 'selected_enemy': None, 'nightmare_enemies': False, 'scale_boss_stats': True, 'cups_bosses': True, 'data_bosses': False, 'remove_damage_cap': False, 'memory_expansion': False}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_seedgen_error3(self):
        options =  {'remove_damage_cap': False, 'cups_give_xp': True, 'retry_data_final_xemnas': True, 'boss': 'One to One', 'selected_boss': 'Final Xemnas', 'nightmare_bosses': False, 'bosses_replace_enemies': False, 'cups_bosses': False, 'data_bosses': False, 'mickey_rule': 'follow', 'enemy': 'Wild', 'nightmare_enemies': False, 'combine_enemy_sizes': True, 'combine_melee_ranged': False, 'memory_expansion': True}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        # Make sure it's valid base64
        base64.decodebytes(b64)

    def test_seedgen_error4(self):
        options = {'remove_damage_cap': False, 'cups_give_xp': False, 'retry_data_final_xemnas': True, 'retry_dark_thorn': False, 'boss': 'One to One', 'nightmare_bosses': False, 'bosses_replace_enemies': False, 'cups_bosses': False, 'data_bosses': True, 'mickey_rule': 'follow', 'enemy': 'One to One', 'nightmare_enemies': False, 'combine_enemy_sizes': False, 'combine_melee_ranged': False, 'memory_expansion': True}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        base64.decodebytes(b64)

    def test_seedgen_error5(self):
        options = {'remove_damage_cap': True, 'cups_give_xp': True, 'retry_data_final_xemnas': True, 'retry_dark_thorn': True, 'boss': 'Disabled', 'nightmare_bosses': False, 'bosses_replace_enemies': False, 'cups_bosses': False, 'data_bosses': False, 'mickey_rule': 'follow', 'enemy': 'One to One', 'nightmare_enemies': False, 'combine_enemy_sizes': False, 'combine_melee_ranged': False, 'memory_expansion': True}
        rando = Randomizer(tempdir=testutils.get_tmp_path())
        b64 = rando.generate_seed("kh2", options=options)
        import base64
        base64.decodebytes(b64)

    def test_getbosses(self):
        kh2 = KingdomHearts2()
        kh2.enemy_manager.create_enemy_records(getavail=True)
        testutils.validate_enemy_records(kh2.enemy_manager.enemy_records)

    def test_enmp(self):
        import yaml
        kh2 = KingdomHearts2()
        with open(os.path.join(os.path.dirname(__file__), "KH2", "data", "enmpVanilla.yml")) as f:
            enmp_data_vanilla = yaml.load(f, Loader=yaml.SafeLoader)
        generated_enmp = ModWriter('.').enmp_manager.dumpEnmpData(enmp_data_vanilla)

    def test_pickbossmapping(self):
        kh2 = KingdomHearts2()
        bosses = kh2.enemy_manager.get_boss_list({})
        mapping = pickbossmapping(kh2.enemy_manager.enemy_records, bosses)
        def getcounts(mapping):
            counts = {}
            maxcounts = 0
            for old, new in mapping.items():
                if new not in counts:
                    counts[new] = 0
                if old not in counts:
                    counts[old] = 0
                counts[new] += 1
            return counts
        counted = getcounts(mapping)
        assert min(counted.values()) == 1
        assert max(counted.values()) == 1

    def validate_memory_expansion(self):
        options = {"enemy": "One to One Per Room", "memory_expansion": True}
        randomization_pc = testutils.generateSeed(options)
        options["memory_expansion"] = False
        randomization_ps2 = testutils.generateSeed(options)
        assert True == testutils.get_room_randomized(randomization_pc, "Agrabah", "The Cave of Wonders: Treasure Room", "b_40")
        assert False == testutils.get_room_randomized(randomization_ps2, "Agrabah", "The Cave of Wonders: Treasure Room", "b_40")

    def test_is_replacement_blocked(self):
        kh2 = KingdomHearts2()
        from khbr.KH2.schemas.enemy_records import get_schema
        source = get_schema()
        source["tags"] = ["rc_blocked"]
        dest = get_schema()
        assert not kh2.enemy_manager.isReplacementBlocked(source, dest)
        dest["tags"] = ["needs_rc"]
        assert kh2.enemy_manager.isReplacementBlocked(source, dest)

    def test_wild_dont_randomize_demyxoc(self):
        options = {"boss": "Wild"}
        randomization = testutils.generateSeed(options)
        assert not testutils.get_randomized(randomization, "Demyx OC")

    def test_vexen_msn_replaced_for_riku(self):
        options = {"selected_boss": "Riku"}
        randomization = testutils.generateSeed(options)
        assert randomization["msn_map"]["HB32_FM_VEX"]["name"] == "WI03_MS104"

    def test_proper_ai_edit_to_setzer(self):
        # [broken_seed, working_seed]
        for seed in ["73724", "60025"]:
            options ={'remove_damage_cap': False, 'cups_give_xp': True, 'retry_data_final_xemnas': True, 'retry_dark_thorn': False, 'remove_cutscenes': 'Disabled', 'party_member_rando': False, 'costume_rando': False, 'revenge_limit_rando': 'Vanilla', 'boss': 'One to One', 'nightmare_bosses': False, 'bosses_replace_enemies': False, 'cups_bosses': True, 'data_bosses': False, 'gimmick_bosses': False, 'sephiroth': False, 'terra': False, 'mickey_rule': 'follow', 'scale_boss_stats': False, 'enemy': 'One to One', 'nightmare_enemies': False, 'separate_nobodys': False, 'combine_enemy_sizes': False, 'combine_melee_ranged': False, 'memory_expansion': True}
            tmppath = testutils.get_tmp_path()
            modpath = os.path.join(tmppath, "setzertest")
            if os.path.exists(modpath):
                shutil.rmtree(modpath)
            rando = Randomizer(tempdir=tmppath, tempfn="setzertest", deletetmp=False)
            b64 = rando.generate_seed("kh2", seed=seed, options=options)
            assert os.path.exists(modpath)
            filepath = os.path.join(modpath, "files", "ai", "TT05_MS405_ms_s.bdscript")
            replacementfilepath = os.path.join(modpath, "files", "ard", "tt05", "b_44.yml")
            assert os.path.exists(filepath)
            assert os.path.exists(replacementfilepath)
            tt05ard = yaml.load(open(replacementfilepath))
            repid = tt05ard[0]["Entities"][3]["ObjectId"]
            bdscript = open(filepath).read().split("\n")
            assert bdscript[118] == " pushImm {}".format(repid), "{} != {}".format(bdscript[118], repid)

    def test_dont_replace_enemy_msns_for_boss(self):
        # TT msns should not be getting placed without enemies
        options = {"boss": "Wild", "cups_bosses": True, "data_bosses": True, "terra": True, "sephiroth": True}
        randomization = testutils.generateSeed(options)
        msns_to_test = [
            "CA09_MEDAL/ca_m.bdscript",
            "TT14_MS109/tt_d.bdscript",
            "TT04_MS301/tt04.bdscript",
        ]
        for msn in msns_to_test:
            assert msn not in randomization.get("ai_mods")
        options["enemy"] =  "One to One"
        randomization2 = testutils.generateSeed(options)
        for msn in msns_to_test:
            assert msn in randomization2.get("ai_mods")
        pass


    def test_gr_room_uses_luxord_msn_when_replaced(self):
        # gr room should still work for luxord
        options = {"selected_boss": "Luxord"}
        randomization = testutils.generateSeed(options)
        assert randomization["msn_map"]["CA01_MS204"]["name"] == "EH14_MS103"
        0/0
        pass

    def test_gr_2_vanilla_works_one_to_one(self):
        # gr 2 when vanilla has no customizations applied
        # Needs the ability to pass in a custom One to One boss replacements list
        pass

    def test_gr_2_vanilla_works_wild(self):
        # gr 2 has the right mods applied to work when vanilla and elsewhere
        pass

    def test_gr_2_blizzard_lord_own_msn(self):
        # gr 2 when blizzard lord replaces should not be using gr2 msn
        pass

    def test_dont_copy_msn_when_ai_mod(self):
        # test on a struggle room, and an enemy room
        pass

    def test_no_change_ambush(self):
        # Ambush is fucked, it should not get changed ever and the area data program should be untouched too
        pass



    # Testing enemies.yaml stuff, probably in it's own file

    def test_behavior_mods(self):
        # test behavior mods are working properly
        pass

    def test_aimods(self):
        # Test ai_mods is getting filled out right for all kinds of ai mods
        # requires a rewrite first to know how they should look
        pass

    def test_unknown_variable_fails(self):
        pass

    def test_replace_as(self):
        pass

    def test_source_replace_allowed(self):
        pass

    def test_msn_replace_allowed(self):
        pass

    def test_tags(self):
        # test all of the different kinds of tags I look at eg organization roxas etc
        pass

    def test_category(self):
        pass
        
    def test_isnightmare(self):
        pass

    def test_child_inherits_parent(self):
        pass

    def test_child_overwrites_parent(self):
        pass

    def test_variationof_inherits_parent(self):
        pass # including variationof childs

    def test_variationof_overwrites_parent(self):
        pass # including variationof childs

    def test_msn_required(self):
        pass

    def test_msn_source_as(self):
        pass

    def test_cmdmods(self):
        pass

    def test_mickey_source(self):
        pass

    def test_sizetag(self):
        pass

    def test_roommaxsize_roomsize_roomsizemultiplier(self):
        pass

    def test_blacklist_whitelist(self):
        pass # test source/destination for both and when both are used


    # Still need to write some good tests for the second half of the generation, and then run coverage to check that everything is covered

# Unit test cases to write

# And coverage

# Uncomment to run a single test through ipython
ut = Tests()
#ut.test_he06_btl_122_should_not_be_edited()
#ut.test_seedgen_enemy_wild_other()
#ut.test_gr_room_uses_luxord_msn_when_replaced()

# Uncomment to run the actual tests
unittest.main()

