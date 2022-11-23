class AiManager:
    def __init__(self, fn, script):
        self.script = script
        self.fn = fn

    def replace(self, original, new):
        self.script = self.script.replace("{"+str(original)+"}", str(new))

    def get_script(self):
        return self.script