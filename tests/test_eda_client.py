from atst.eda_client import MockEDAClient, parse_eda_xml


mock_client = MockEDAClient()


def test_list_contracts():
    results = mock_client.list_contracts()
    assert len(results) == 3


def test_get_contract():
    result = mock_client.get_contract("DCA10096D0052", "y")
    assert result["contract_no"] == "DCA10096D0052"
    assert result["amount"] == 2_000_000


def test_contract_not_found():
    result = mock_client.get_contract("abc", "y")
    assert result is None


def test_eda_xml_parser():
    with open("tests/fixtures/eda_contract.xml") as contract:
        eda_data = parse_eda_xml(contract.read())
        assert eda_data["clin_0001"] == 200000.00
        assert not eda_data["clin_0003"]
