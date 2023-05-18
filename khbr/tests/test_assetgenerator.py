from khbr.KH2.AssetGenerator import AssetGenerator

def test_find_asset():
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
