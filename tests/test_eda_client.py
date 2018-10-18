from atst.eda_client import MockEDAClient, parse_eda_xml


mock_client = MockEDAClient()


def test_list_contracts():
    results = mock_client.list_contracts()
    assert len(results) == 3


def test_get_contract():
    result = mock_client.get_contract("DCA10096D0052", "y")
    assert result["number"] == "DCA10096D0052"


def test_contract_not_found():
    result = mock_client.get_contract("abc", "y")
    assert result is None


def test_eda_xml_parser():
    with open("tests/fixtures/eda_contract.xml") as contract:
        eda_data = parse_eda_xml(contract.read())
        assert eda_data["clin_0001"] == 200_000.00
        assert not eda_data["clin_0003"]


_EDA_XML_NO_NUMBER = """
<ProcurementDocument>
  <AwardInstrument>
    <ContractLineItems>
      <LineItems>
        <LineItemIdentifier>
          <DFARS>
            <LineItem>
              <LineItemType>CLIN</LineItemType>
              <LineItemBase>0001</LineItemBase>
            </LineItem>
          </DFARS>
        </LineItemIdentifier>
        <LineItemAmounts>
          <ItemOtherAmounts>
            <AmountDescription>Not to Exceed Amount (Funding)</AmountDescription>
            <Amount>not a number</Amount>
          </ItemOtherAmounts>
        </LineItemAmounts>
      </LineItems>
    </ContractLineItems>
  </AwardInstrument>
</ProcurementDocument>
"""


def test_eda_xml_parser_with_bad_xml():
    eda_data = parse_eda_xml(_EDA_XML_NO_NUMBER)
    assert eda_data["clin_0001"] is None
