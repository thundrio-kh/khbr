import os

class LuaManager:
    def __init__(self, name):
        self.luamod = name

    def create_file(self):
        print("hit")
        if self.luamod == "final_xemnas":
            self.create_final_xemnas()
        
    def create_final_xemnas(self):
        with open(os.path.join(os.path.dirname(__file__), "data", "lua_mods", "final_xemnas")) as f:
            self.data = f.read()
        self.fn = "final_xemnas_dome_skip_anywhere.lua"

