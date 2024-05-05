import unittest, os


class Tests(unittest.TestCase):
    def test_replace(self):
        ai = AiManager("name", "this is a {settest} script")
        ai.replace("settest", 5)
        assert ai.get_script() == "this is a 5 script"



# Uncomment to run a single test through ipython
ut = Tests()
#ut.test_add_spawn()
#ut.test_set_jump()
#ut.test_set_open_menu()

# Uncomment to run the actual tests
unittest.main()
