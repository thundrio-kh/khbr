from khbr.randutils import log_output

class AreaDataProgram:
    def __init__(self, lines, moose=False):
        self.lines = lines
        self.moose = moose
        num_settings = len(''.join(lines).split("AreaSettings"))
        # if num_settings > 2:
        #     log_output(lines)
        self.map = self.map_program()
    def make_program(self):
        return '\n'.join(self.lines)
    def map_program(self):
        smap = {}
        for l in range(len(self.lines)):
            line = self.lines[l]
            word = line.strip().split(" ")[0] 
            if not word in smap:
                smap[word] = [l]
            else:
                smap[word].append(l) # I THINK this only happens with If statements and really only the colloseum so don't really have to worry about this case
        return smap
    def has_command(self, command):
        return command in self.map
    def get_command(self, command, return_all=False):
        values = []
        if self.has_command(command):
            for l in self.map[command]:
                values.append(self.lines[l].replace(command, "").strip())
        if return_all:
            return values
        return values[0] if values else ""
    def add_command(self, command, parameters, set_for_settings=None):
        '''command is a word, parameters is a string'''
        '''adds not SetX comma'''
        newline = f"{command} {parameters}"
        if command.startswith("Set"):
            newline = "\t"+newline
        if self.has_command(command):
            change_lines = self.map[command]
            if set_for_settings:
                change_lines = []
                for i in set_for_settings:
                    change_lines.append(self.map[command][i])
            for l in change_lines:
                self.lines[l] = newline
        else:
            if not command.startswith("Set"):
                # There might be something here where you need to find the first empty line and add before that
                self.lines.insert(1,newline)
            else:
                # Find the last "Set" line
                f = 0
                for l in range(len(self.lines)):
                    line = self.lines[l]
                    if line.strip().startswith("Set"):
                        log_output(line)
                        f = l
                self.lines.insert(f+1, newline)
        self.map = self.map_program()
    def add_line(self, line):
        self.lines.append(line)
        self.map = self.map_program()
    def remove_command(self, command):
        if not self.has_command(command):
            return
        lines_to_pop = self.map[command]
        for l in lines_to_pop[::-1]:
            self.lines.pop(l)
        self.map = self.map_program()
    def add_packet_spec(self, packet_size=0x100000/2):
        self.add_command("AllocPacket", str(int(packet_size)))
    def add_enemy_spec(self, enemy_size=0x200000):
        self.add_command("AllocEnemy", str(int(enemy_size)))
    def get_mission(self):
        if not self.has_command("Mission"):
            return False
        return self.get_command("Mission").split(" ")[-1].replace('"','')
    def update_capacity(self, capacity=None):
        if self.moose:
            self.remove_command("Capacity")
        elif capacity:
            self.add_command("Capacity", str(capacity))
    def set_jump(self, world, room, program, fadetype="16386", jumptype="2", entrance="0", set_for_settings=None):
        # TODO make this print a warning and not do anything if there is no existing jump
        parameters = f"Type {jumptype} World {world} Area {room} Entrance {entrance} LocalSet {program} FadeType {fadetype}"
        if self.has_command("SetJump"):
            self.add_command("SetJump", parameters, set_for_settings)
        else:
            log_output("Trying to SetJump on a program that does not have one is not allowed")
    def set_open_menu(self, open_menu):
        if open_menu:
            self.add_command("SetPartyMenu", "1")
            self.add_command("SetMember", "3")
        else:
            self.add_command("SetPartyMenu", "0")
    def remove_event(self):
        self.remove_command("SetEvent")
    def set_flags(self, flags=None):
        if not flags:
            flags = []
        existingflags = self.get_command("SetProgressFlag")
        if existingflags:
            flags += existingflags.split(" ")
        parameters = " ".join([f for f in flags])
        self.add_command("SetProgressFlag", parameters)
    def set_area_settings(self, x, y):
        self.add_command("AreaSettings", f"{x} {y}")