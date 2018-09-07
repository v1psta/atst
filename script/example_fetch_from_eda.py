from atst.app import make_config, make_app
from atst.eda_client import EDAClient


config = make_config()

client = EDAClient(
    base_url=config.get("EDA_HOST"),
    user_name=config.get("EDA_USER_NAME"),
    user_role=config.get("EDA_USER_ROLE"),
    auth_name=config.get("EDA_AUTH_NAME"),
    auth_pass=config.get("EDA_AUTH_PASS"),
)

contract_number = "DCA10096D0052"

listed = client.list_contracts(
    contract_number=contract_number,
    delivery_order="",
    cage_code="1U305",
    duns_number="",
)
contract = client.get_contract(contract_number=contract_number, status="Y")

requested_clins = ",".join(["'0001'", "'0003'", "'1001'", "'1003'", "'2001'", "'2003'"])
clins = client.get_clins(
    record_key=contract_number, duns_number="", cage_code="1U305", clins=requested_clins
)
