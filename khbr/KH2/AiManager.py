import re

class AiManager:
    def __init__(self, fn, script):
        self.script = script
        self.fn = fn

    def replace(self, original, new):
        self.script = self.script.replace("{"+str(original)+"}", str(new))

    def set_karma_limit(self, available_values):
        karma_param = re.compile(r'pushImmf (.*)\n.*; trap_enemy_set_karma_limit')
        if karma_param.search(self.script):
            self.script = karma_param.sub(lambda m: "pushImmf {}\n syscall 2, 76 ; trap_enemy_set_karma_limit ".format(str(available_values.pop())),  self.script)
            return
        return
    
    def add_when_dead(self, lines):
        str_to_add = ': ; dead\n popToSp 0\n'+'\n'.join(lines)
        dead_param = re.compile(r': ;___label for action pushFromPAi.*? ; ___ai (dead\n popToSp 0)')
        if dead_param.search(self.script):
            self.script = dead_param.sub(lambda m: str_to_add, self.script)
        else:
            raise Exception("Error: Can not find dead action for {}".format(self.fn))

    def drop_dataspace_orbs(self):
        self.add_when_dead([
            ' pushFromFSp 0',
            ' pushImm 10',
            ' syscall 1, 278 ; trap_obj_scatter_prize_tr'
        ])

    def get_script(self):
        return self.script
    
# IS_HADES_ESCAPE:
#  syscall 1, 23 ; trap_area_world
#  pushImm 6
#  sub
#  eqz
#  jz RET_FALSE
#  syscall 1, 24 ; trap_area_area
#  pushImm 5
#  sub
#  eqz
#  jz RET_FALSE
#  syscall 1, 26 ; trap_area_battle_set
#  pushImm 111
#  sub
#  eqz
#  jz RET_FALSE
#  jmp RET_TRUE