from khbr.KH2.AiManager import AiManager

def test_replace():
    ai = AiManager("name", "this is a {settest} script")
    ai.replace("settest", 5)
    assert ai.get_script() == "this is a 5 script"

def test_replace_not_found():
    ai = AiManager("name", "this is a settest script")
    ai.replace("settest", 5)
    assert ai.get_script() == "this is a settest script"

def test_modify_karma_limit():
    ai = AiManager("test_set_karma_limit.asm", """ pushFromFSp 0
 pushImmf 92
 syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)
 jmp L4969
L4930:
 pushFromFSp 0""")
    available_values = [3]
    ai.set_karma_limit(available_values)
    assert len(available_values) == 0


def test_modify_multiple_karma_limit():
    ai = AiManager("test_set_multiple_karma_limit.asm", """ pushFromFSp 0
 pushImmf 92
 syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)
 jmp L4969
L4930:
 pushFromFSp 0
 pushImmf 92
 syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)""")
    available_values = [3, 5, 7]
    ai.set_karma_limit(available_values)
    assert available_values == [3]
    assert ai.get_script() == """ pushFromFSp 0
 pushImmf 7
 syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)
 jmp L4969
L4930:
 pushFromFSp 0
 pushImmf 5
 syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)"""

def test_add_karma_limit():
    ai = AiManager("test_add_karma_limit.asm", """ pushImm 0
 pushImm 0
 syscall 1, 6 ; trap_act_table_add (12 in, 0 out)
 pushFromPWp W436
 pushFromPAi L14012 ; ___ai leave (L14012)
 pushImm 196908
 pushImm L5389
 pushImm 0
 pushImm 0""")
    available_values = [1,2,3,4,5]
    ai.set_karma_limit(available_values)
    assert available_values == [1,2,3,4]
    assert ai.get_script() == """ pushImm 0
 pushImm 0
 syscall 1, 6 ; trap_act_table_add (12 in, 0 out)
 pushFromFSp 0
 pushImmf 5
 syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)
 pushFromPWp W436
 pushFromPAi L14012 ; ___ai leave (L14012)
 pushImm 196908
 pushImm L5389
 pushImm 0
 pushImm 0"""