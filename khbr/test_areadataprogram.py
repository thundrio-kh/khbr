import unittest
from khbr.KH2.AreaDataProgram import AreaDataProgram

class Tests(unittest.TestCase):
    def test_make_program(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        output = adp.make_program()
        assert output.split("\n") == lines
    def test_has_command(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        assert adp.has_command("Bgm") == True
        assert adp.has_command("Spawn") == False
        assert adp.has_command("SetProgressFlag") == True
        assert adp.has_command("SetJump") == False
    def test_get_command(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        assert adp.get_command("SetProgressFlag") == "0x1841"
    def test_add_command(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        adp.add_command("Spawn", "0a")
        adp.add_command("Bgm", "999 999")
        adp.add_command("SetProgressFlag", "0x1")
        adp.add_command("SetTest", "abc")
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Spawn 0a",
            "Bgm 999 999",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1",
            "\tSetTest abc"
        ]
    def test_remove_command(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841",
            "\tSetEvent ewww",
            "\tSetTest abc"
        ]
        adp = AreaDataProgram(lines)
        adp.remove_command("Bgm")
        adp.remove_command("SetEvent")
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841",
            "\tSetTest abc"
        ]
    def test_add_packet_spec(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        adp.add_packet_spec()
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "AllocPacket 524288",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
    def test_add_enemy_spec(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        adp.add_enemy_spec()
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "AllocEnemy 2097152",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
    def test_set_area_settings(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        adp.set_area_settings(16, -1)
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 16 -1",
            "\tSetProgressFlag 0x1841"
        ]
    def test_get_mission(self):
        lines = [
            "Program 0x3B",
            "Party W_FRIEND",
            "Mission 0x44 \"AL03_MS103\"",
            "Spawn \"b_40\""
        ]
        adp = AreaDataProgram(lines)
        output = adp.get_mission()
        assert output == "AL03_MS103"
    def test_update_capacity(self):
        lines = [
            "Program 0xBF",
            "Capacity 50",
            "Spawn 3"
        ]
        adp = AreaDataProgram(lines, moose=True)
        adp.update_capacity(capacity=99)
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Spawn 3"
        ]
        adp = AreaDataProgram(lines, moose=False)
        adp.update_capacity(capacity=99)
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Capacity 99",
            "Spawn 3"
        ]
        lines = [
            "Program 0xBF",
            "Spawn 3"
        ]
        adp = AreaDataProgram(lines, moose=True)
        adp.update_capacity(capacity=99)
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Spawn 3"
        ]
    def test_set_jump(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        adp.set_jump(world="AA", room="01", program="02", fadetype="03", jumptype="04", entrance="05")
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841",
            "\tSetJump Type 04 World BB Area 01 Entrance 05 LocalSet 02 FadeType 03"
        ]
        adp = AreaDataProgram(lines)
        adp.set_jump(world="AA", room="01", program="02", fadetype="03", jumptype="04", entrance="05")
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841",
            "\tSetJump Type 04 World AA Area 01 Entrance 05 LocalSet 02 FadeType 03"
        ]
    def test_set_open_menu(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841",
            "\tSetPartyMenu 0"
        ]
        adp = AreaDataProgram(lines)
        adp.set_open_menu(True)
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841",
            "\tSetPartyMenu 1",
            "\tSetMember 3"
        ]
        adp.set_open_menu(False)
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841",
            "\tSetPartyMenu 0",
            "\tSetMember 3"
        ]
    def test_remove_event(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetEvent abc",
            "\tSetProgressFlag 0x1841"
        ]
        adp = AreaDataProgram(lines)
        adp.remove_event()
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetProgressFlag 0x1841"
        ]
    def test_set_flags(self):
        lines = [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetEvent abc"
        ]
        adp = AreaDataProgram(lines)
        adp.set_flags(['0x1'])
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetEvent abc",
            "\tSetProgressFlag 0x1"
        ]
        adp.set_flags(['0x2'])
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0xBF",
            "Bgm 120 120",
            "AreaSettings 7 10",
            "\tSetEvent abc",
            "\tSetProgressFlag 0x2 0x1"
        ]
    def test_get_multi_settings_program(self):
        prg = """Program 0x4C
Bgm 119 119
AreaSettings 9 -1
	SetProgressFlag 0x821
	SetUnk05 0x3
	SetEvent "110a" Type 129
	SetPartyMenu 0

AreaSettings 10 -1
	SetProgressFlag 0x821
	SetUnk05 0x3
	SetEvent "110b" Type 129
	SetPartyMenu 0

AreaSettings 11 -1
	SetProgressFlag 0x821
	SetUnk05 0x3
	SetEvent "110c" Type 129
	SetPartyMenu 0

AreaSettings 76 -1
	SetEvent "110" Type 1
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 77 FadeType 1
	SetPartyMenu 0"""
         
        adp = AreaDataProgram(prg.split("\n"))
        output = adp.make_program()
        assert output == prg
        events_list = adp.get_command("SetEvent", return_all=True)
        events_list_copy = list(events_list)
        assert len(events_list) == 4
        found = 0
        for l in ['"110a"', '"110b"', '"110c"', '"110"']:
            for e in range(len(events_list_copy)):
                if l in events_list_copy[e]:
                    found += 1
        assert found == 4
    def test_setup_multiple_jumps(self):
        prg = """Program 0x54
Bgm 119 119
AreaSettings 8 -1
	SetProgressFlag 0x85A
	SetUnk05 0x3
	SetJump Type 1 World TT Area 5 Entrance 51 LocalSet 0 FadeType 1
	SetPartyMenu 0

AreaSettings 7 -1
	SetProgressFlag 0x85B
	SetUnk05 0x3
	SetEvent "406" Type 19
	SetJump Type 1 World TT Area 5 Entrance 52 LocalSet 0 FadeType 1
	SetPartyMenu 0"""
        
        adp = AreaDataProgram(prg.split("\n"))
        output = adp.make_program()
        assert output == prg
        adp.set_jump(world="AA", room="01", program="02", fadetype="03", jumptype="04", entrance="05")
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0x54",
            "Bgm 119 119",
            "AreaSettings 8 -1",
            "\tSetProgressFlag 0x85A",
            "\tSetUnk05 0x3",
            "\tSetJump Type 04 World AA Area 01 Entrance 05 LocalSet 02 FadeType 03",
            "\tSetPartyMenu 0",
            "",
            "AreaSettings 7 -1",
            "\tSetProgressFlag 0x85B",
            "\tSetUnk05 0x3",
            "\tSetEvent \"406\" Type 19",
            "\tSetJump Type 04 World AA Area 01 Entrance 05 LocalSet 02 FadeType 03",
            "\tSetPartyMenu 0"
        ]
        
        adp = AreaDataProgram(prg.split("\n"))
        adp.set_jump(world="AA", room="01", program="02", fadetype="03", jumptype="04", entrance="05", set_for_settings=[0])
        
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0x54",
            "Bgm 119 119",
            "AreaSettings 8 -1",
            "\tSetProgressFlag 0x85A",
            "\tSetUnk05 0x3",
            "\tSetJump Type 04 World AA Area 01 Entrance 05 LocalSet 02 FadeType 03",
            "\tSetPartyMenu 0",
            "",
            "AreaSettings 7 -1",
            "\tSetProgressFlag 0x85B",
            "\tSetUnk05 0x3",
            "\tSetEvent \"406\" Type 19",
            "\tSetJump Type 1 World TT Area 5 Entrance 52 LocalSet 0 FadeType 1",
            "\tSetPartyMenu 0"
        ]

        adp = AreaDataProgram(prg.split("\n"))
        adp.set_jump(world="AA", room="01", program="02", fadetype="03", jumptype="04", entrance="05", set_for_settings=[1])
        
        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0x54",
            "Bgm 119 119",
            "AreaSettings 8 -1",
            "\tSetProgressFlag 0x85A",
            "\tSetUnk05 0x3",
            "\tSetJump Type 1 World TT Area 5 Entrance 51 LocalSet 0 FadeType 1",
            "\tSetPartyMenu 0",
            "",
            "AreaSettings 7 -1",
            "\tSetProgressFlag 0x85B",
            "\tSetUnk05 0x3",
            "\tSetEvent \"406\" Type 19",
            "\tSetJump Type 04 World AA Area 01 Entrance 05 LocalSet 02 FadeType 03",
            "\tSetPartyMenu 0"
        ]

        prg = """Program 0x55
Bgm 119 119
AreaSettings 8 -1
	SetProgressFlag 0x85D
	SetUnk05 0x3
	SetJump Type 1 World TT Area 5 Entrance 53 LocalSet 0 FadeType 1
	SetPartyMenu 0

AreaSettings 7 -1
	SetProgressFlag 0x85E
	SetUnk05 0x3
	SetEvent "408" Type 19
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 86 FadeType 1
	SetPartyMenu 0"""
        
        adp = AreaDataProgram(prg.split("\n"))
        adp.set_jump(world = "TT", room="5", program="0", jumptype="1", entrance="53", fadetype="0", set_for_settings=[0])
        adp.set_jump(world = "TT", room="0", program="86", jumptype="2", entrance="0", fadetype="0", set_for_settings=[1])

        output = adp.make_program()
        assert output.split("\n") == [
            "Program 0x55",
            "Bgm 119 119",
            "AreaSettings 8 -1",
        	"\tSetProgressFlag 0x85D",
        	"\tSetUnk05 0x3",
        	"\tSetJump Type 1 World TT Area 5 Entrance 53 LocalSet 0 FadeType 0",
	        "\tSetPartyMenu 0",
            "",
            "AreaSettings 7 -1",
        	"\tSetProgressFlag 0x85E",
	        "\tSetUnk05 0x3",
	        "\tSetEvent \"408\" Type 19",
	        "\tSetJump Type 2 World TT Area 0 Entrance 0 LocalSet 86 FadeType 0",
	        "\tSetPartyMenu 0"

        ]

# There are a few programs with more than one area settings (I wonder how many?), and I'm not parsing those correctly

# TODO in order to support "chain logic" of removing cutscenes, I'll need to implement additions to add_command
# Uncomment to run a single test through ipython
ut = Tests()
ut.test_setup_multiple_jumps()
#ut.test_set_jump()
#ut.test_set_open_menu()


# Uncomment to run the actual tests
#unittest.main()
