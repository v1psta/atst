from atst.eda_client import MockEDAClient


client = MockEDAClient()


def test_list_contracts():
    results = client.list_contracts()
    assert len(results) == 3


def test_get_contract():
    result = client.get_contract("DCA10096D0052", "y")
    assert result["contract_no"] == "DCA10096D0052"
    assert result["amount"] == 2000000


def test_contract_not_found():
    result = client.get_contract("abc", "y")
    assert result is None
