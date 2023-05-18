from khbr.KH2.AreaDataScript import AreaDataScript

def test_one_program_script():
    script = """Program 0xCD
Spawn "d53_"
Spawn "e53_"
Spawn "f53_" """
    sc = AreaDataScript(script)
    assert len(sc.programs) == 1

def test_multi_program_script():
    script = """Program 0xCD
Spawn "d53_"
Spawn "e53_"
Spawn "f53_"

Program 0xEA
Bgm Default Default
AreaSettings 0 -1
	SetEvent "112" Type 66
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 235 FadeType 1
	SetPartyMenu 0

    pass"""
    sc = AreaDataScript(script)
    assert len(sc.programs) == 2

def test_complex_program_script():
    script = """Program 0x15
Spawn "e_50"

Program 0x4D
Bgm 119 119
AreaSettings 37 -1
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 77 FadeType -1
	SetPartyMenu 0

AreaSettings 38 -1
	SetProgressFlag 0x822
	SetEvent "111" Type 1
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 78 FadeType 1
	SetPartyMenu 0

AreaSettings 15 -1
	SetProgressFlag 0x822
	SetUnk05 0x3
	SetEvent "111" Type 9
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 78 FadeType 1
	SetPartyMenu 0

Spawn "a11_"
Spawn "b11_"
Spawn "c11_"
Spawn "e11_"
Spawn "f11_"
Spawn "h11_"

Program 0x16
AreaSettings 9 -1
	SetProgressFlag 0x8EF
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 182 FadeType 1
	SetPartyMenu 0

AreaSettings 10 -1
	SetProgressFlag 0x8F0
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 183 FadeType 1
	SetPartyMenu 0

AreaSettings 11 -1
	SetProgressFlag 0x8F1
	SetJump Type 2 World TT Area 0 Entrance 0 LocalSet 184 FadeType 1
	SetPartyMenu 0

AreaSettings 161 -1
	SetUnk05 0x1
	SetJump Type 2 World HB Area 0 Entrance 0 LocalSet 122 FadeType 1
	SetPartyMenu 0

Spawn "e_50"
Spawn "d70_"
Spawn "e70_"
Spawn "f70_"
Spawn "y73_"

Program 0x00
Spawn "e_50"
"""
    sc = AreaDataScript(script)
    assert len(sc.programs) == 4

def test_get_program():
    script = """Program 0xCD
Spawn "d53_"
Spawn "e53_"
Spawn "f53_" """
    sc = AreaDataScript(script)
    assert sc.get_program(0xCD) == list(sc.programs.values())[0]
    assert sc.get_program(9999) == None