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
            self.script = karma_param.sub(lambda m: "pushImmf {}\n syscall 2, 76 ; trap_enemy_set_karma_limit".format(str(available_values.pop())),  self.script)
            return
        act_table_syscall = re.compile(r'\n.*; trap_act_table_add \(12 in, 0 out\)(\n)')
        if act_table_syscall.search(self.script):
            self.script = act_table_syscall.sub(lambda m: "\n syscall 1, 6 ; trap_act_table_add (12 in, 0 out)\n pushFromFSp 0\n pushImmf {}\n syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)\n".format(str(available_values.pop())), self.script, count=1)
        return

    def get_script(self):
        return self.script
