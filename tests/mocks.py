from tests.factories import RequestFactory, UserFactory


MOCK_USER = UserFactory.build()
MOCK_REQUEST = RequestFactory.build(creator=MOCK_USER)
DOD_SDN_INFO = {"first_name": "ART", "last_name": "GARFUNKEL", "dod_id": "5892460358"}
DOD_SDN = f"CN={DOD_SDN_INFO['last_name']}.{DOD_SDN_INFO['first_name']}.G.{DOD_SDN_INFO['dod_id']},OU=OTHER,OU=PKI,OU=DoD,O=U.S. Government,C=US"

MOCK_VALID_PE_ID = "080675309U"

FIXTURE_EMAIL_ADDRESS = "artgarfunkel@uso.mil"

PDF_FILENAME = "tests/fixtures/sample.pdf"
PDF_FILENAME2 = "tests/fixtures/sample2.pdf"
