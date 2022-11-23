from khbr.KH2.AreaDataProgram import AreaDataProgram


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
                    programs[currentProgram] = AreaDataProgram(lines_program, ispc=self.ispc)
                currentProgram = int(line.split(" ")[1], 16)
                lines_program = [line]
            else:
                lines_program.append(line)
        if currentProgram:
            programs[currentProgram] = AreaDataProgram(lines_program, ispc=self.ispc)
        return programs
    def get_program(self, number):
        if number not in self.programs:
            raise Exception("Program not found")
        return self.programs[number]