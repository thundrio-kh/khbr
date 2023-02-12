import unittest
from khbr.KH2.schemas.enemyseed import EnemySeed
import testutils

class Tests(unittest.TestCase):
    def test_add_spawn(self):
        conf = testutils.get_random_config()
        es = EnemySeed(config=conf)
        assert es.spawns == {}
        es.add_spawn(
            world="wtest",
            room="rtest",
            spawnpoint="sptest",
            spid="unittest",
            entity={"name": "old", "var": 5},
            new_boss_object={"name": "test"}
        )
        assert es.spawns == {'wtest': {'rtest': {'spawnpoints': {'sptest': {'sp_ids': {'unittest': [{'name': 'test', 'var': 5}]}}}}}}

# Uncomment to run a single test through ipython
ut = Tests()
#ut.test_add_spawn()
#ut.test_set_jump()
#ut.test_set_open_menu()


# Uncomment to run the actual tests
unittest.main()
