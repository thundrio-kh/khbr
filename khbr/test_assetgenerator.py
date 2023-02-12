import unittest
from khbr.KH2.AssetGenerator import AssetGenerator
import testutils

class Tests(unittest.TestCase):
    def test_find_asset(self):
        ag = AssetGenerator(modwriter=None)
        assert len(ag.assets) == 0
        # Test finding an asset that doesn't exist without default
        assert ag.find_asset("test") == None
        assert len(ag.assets) == 0
        # Test finding asset that doesn't exist with default\
        assert ag.find_asset("test", default={"name": "test2"}) == {"name": "test2"}
        assert len(ag.assets) == 1
        # Test finding asset that does exist without default
        assert ag.find_asset("test2") == {"name": "test2"}
        assert len(ag.assets) == 1
        # Test finding asset that does exist with default
        assert ag.find_asset("test2", default={"name": "test2"}) == {"name": "test2"}
        assert len(ag.assets) == 1

# Uncomment to run a single test through ipython
ut = Tests()
ut.test_find_asset()
#ut.test_set_jump()
#ut.test_set_open_menu()


# Uncomment to run the actual tests
unittest.main()
