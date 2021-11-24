class AreaDataScript:
    def __init__(self, txt, ispc=False):
        self.script = txt
        self.ispc = ispc
        self.programs = self.parse_programs(self.script)
    def parse_programs(self, script):
        programs = {}
        currentProgram = None
        lines_program = []
        for line in script.split("\n"):
            if line.startswith("Program"):
                if currentProgram:
                    programs[currentProgram] = lines_program
                currentProgram = int(line.split(" ")[1], 16)
                lines_program = [line]
            else:
                lines_program.append(line)
        if currentProgram:
            programs[currentProgram] = lines_program
        return programs
    def get_program(self, number):
        if number not in self.programs:
            raise Exception("Program not found")
        return '\n'.join(self.programs[number])
    def add_packet_spec(self, number):
        program = [self.get_program(number).split("\n")[0]] + ["AllocPacket {}".format(int(0x100000 / 2))] + self.get_program(number).split("\n")[1:]
        self.programs[number] = program
    def update_program(self, number, capacity=None):
        program = self.get_program(number).split("\n")
        topop = []
        for l in range(len(program)):
            line = program[l]
            if capacity and "Capacity" in line:
                if self.ispc:
                    topop.append(l)
                    continue
                cap_line = line.split(" ")
                cap_line[1] = capacity
                program[l] = ' '.join(cap_line)
        if self.ispc:
            for p in topop[::-1]:
                program.pop(p)
        self.programs[number] = program
    def has_capacity(self, number):
        program = self.get_program(number)
        for line in program.split("\n"):
            if "Capacity" in line:
                return True
        return False
    def has_mission(self, number):
        program = self.get_program(number)
        for line in program.split("\n"):
            if "Mission" in line:
                return True
        return False
    def get_mission(self, number):
        if not self.has_mission(number):
            return None
        program = self.get_program(number)
        for line in program.split("\n"):
            if "Mission" in line:
                return line.split(" ")[-1]