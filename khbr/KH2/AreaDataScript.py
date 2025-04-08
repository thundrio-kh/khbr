from khbr.KH2.AreaDataProgram import AreaDataProgram


class AreaDataScript:
    def __init__(self, txt, moose=False):
        self.script = txt
        self.moose = moose
        self.programs = self.parse_programs(self.script)
    def parse_programs(self, script):
        programs = {}
        currentProgram = None
        lines_program = []
        for line in script.split("\n"):
            if line.startswith("Program"):
                if currentProgram:
                    programs[currentProgram] = AreaDataProgram(lines_program, moose=self.moose)
                currentProgram = int(line.split(" ")[1], 16)
                lines_program = [line]
            else:
                lines_program.append(line)
        if currentProgram:
            programs[currentProgram] = AreaDataProgram(lines_program, moose=self.moose)
        return programs
    def get_program(self, number):
        if number not in self.programs:
            return None
        return self.programs[number]