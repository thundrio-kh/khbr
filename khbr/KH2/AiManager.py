import re


class AiManager:
    def __init__(self, fn, script):
        self.script = script
        self.fn = fn
        self.rooms = {} # Will be filled in with all the rooms the boss is in

    def replace(self, original, new):
        # add actually grabbing variable names like roomData.bossX
        # add basic math after the fact ie - 200
        # add defaults when new=None | 0 (and super default of 0)
        self.script = self.script.replace("{"+str(original)+"}", str(new))

    def set_karma_limit(self, available_values):
        karma_param = re.compile(r'pushImmf (.*)\n.*; trap_enemy_set_karma_limit')
        if karma_param.search(self.script):
            self.script = karma_param.sub(lambda m: "pushImmf {}\n syscall 2, 76 ; trap_enemy_set_karma_limit ".format(str(available_values.pop())),  self.script)
            return
        act_table_syscall = re.compile(r'\n.*; trap_act_table_add \(12 in, 0 out\)(\n)')
        if act_table_syscall.search(self.script):
            self.script = act_table_syscall.sub(lambda m: "\n syscall 1, 6 ; trap_act_table_add (12 in, 0 out)\n pushFromFSp 0\n pushImmf {}\n syscall 2, 76 ; trap_enemy_set_karma_limit \n".format(str(available_values.pop())), self.script, count=1)
        return

    def get_script(self):
        return self.script
    
#     def createFunctionLabel(self, name, function_content):
#         # pushImmf {roomData.bossX | 0}
#         # pushImmf {roomData.bossY - 200 | 0}
#         # pushImmf {roomData.bossZ | 0}
#         find_function = '''Find{label}:
#  syscall 1, 23 ; trap_area_world (0 in, 1 out)
#  pushImm 100
#  mul ; multiply result by 100 to create unique number when combined with room
#  syscall 1, 24 ; trap_area_area (0 in, 1 out)
#  add ; world + room
# '''.format(label=name)
#         for k, v in self.rooms:
#             alphaname = ''.join([c for c in k if c.isalpha()])
#             find_function += ''' dup
#  pushImm {worldroom} ; {bossname} room
#  sub
#  jz {label}{bossname}
# '''.format(ADDSTUFFHERE)
#         find_function += ''' syscall 0, 60 ; nop trap_assert, aka pop unused dup value from top of stack
#  jmp StartPositionDefault
# '''
#         find_function += '''

# '''



# StartPositionDefault:
#  pushImmf 0
#  pushImmf 0
#  pushImmf 0
#  ret
# StartPositionVexen:
#  syscall 0, 60 ; trap_assert, does nothing... but got to reset the stack, one dup
#  pushImmf -13
#  pushImmf -201
#  pushImmf -2092
#  ret
# StartPositionPrisonKeeper:
#  pushImmf 416 ; X
#  pushImmf -204 ; Y
#  pushImmf -923 ; Z
#  ret 
# FindStartPosition:
#  syscall 1, 23 ; trap_area_world (0 in, 1 out)   2
#  pushImm 100                                   ; 100
#  mul ; multiply result by 100                  ; 200
#  syscall 1, 24 ; trap_area_area (0 in, 1 out)  ; 12 
#  add ; world + room                            ; 212
#  dup                                           ; 212
#  pushImm 432 ; vexen room                      ; 432
#  sub                                           ; 220
#  jz StartPositionVexen                         ; 212
#  ; no need to dup last one ?                
#  pushImm 1403                                  ; 1403
#  sub                                           ; -1191
#  jz StartPositionPrisonKeeper
#  jmp StartPositionDefault ; I think this won't work because then you have to jump back

# gosub 4, FindStartPosition




#  {setFunction StartPosition}
#  pushImmf {roomData.bossX} 
#  pushImmf {roomData.bossY - 200}
#  pushImmf {roomData.bossZ}
#  {endFunction}