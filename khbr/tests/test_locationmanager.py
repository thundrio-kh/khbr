from khbr.KH2.schemas.enemyseed import EnemySeed
import testutils

def test_add_spawn():
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