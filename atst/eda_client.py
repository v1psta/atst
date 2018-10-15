from csv import DictReader
import defusedxml.ElementTree as ET

import requests
from requests.auth import HTTPBasicAuth


class EDAClientBase(object):
    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        """
        Get a list of all contracts matching the given filters.
        """
        raise NotImplementedError()

    def get_contract(self, contract_number, status):
        """
        Get details for a contract.
        """
        raise NotImplementedError()


class MockEDAClient(EDAClientBase):
    def __init__(self, *args, **kwargs):
        pass

    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        return [
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
        ]

    MOCK_CONTRACT_NUMBER = "DCA10096D0052"

    # TODO: It seems likely that this will have to supply CLIN data form the
    # EDA returnclinXML API call, in addition to the basic task order data
    # below. See the EDA docs.
    def get_contract(self, contract_number, status):
        if contract_number == self.MOCK_CONTRACT_NUMBER and status == "y":
            return {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
                "amount": 2_000_000,
            }
        else:
            return None


class EDAClient(EDAClientBase):
    def __init__(self, base_url, user_name, user_role, auth_name, auth_pass):
        self.base_url = base_url
        self.user_name = user_name
        self.user_role = user_role
        self.auth = HTTPBasicAuth(auth_name, auth_pass)

    def _make_url(self, method, **kwargs):
        query_args = dict(kwargs)
        query_string = "&".join(
            ["{}={}".format(key, value) for key, value in query_args.items()]
        )
        return "{base_url}/{method}?{query_string}".format(
            base_url=self.base_url, method=method, query_string=query_string
        )

    def _get(self, method, **kwargs):
        url = self._make_url(method, **kwargs)
        return requests.get(url, auth=self.auth, verify="ssl/server-certs/eda.pem")

    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        response = self._get(
            "wawf_interface.returnContractList",
            pContract=contract_number,
            pDelivery_Order=delivery_order,
            pCage_Code=cage_code,
            pDuns_Number=duns_number,
            pUserName=self.user_name,
            pUser_Role=self.user_role,
        )
        lines = response.text.replace("<br />", "").split("\n")
        return list(DictReader(lines))

    def get_contract(self, contract_number, status):
        response = self._get(
            "pds_contract_interface.get_xml_doc",
            pContract=contract_number,
            pStatus=status,
        )
        if response.text.startswith("No data found"):
            return None
        return ET.fromstring(response.text)

    def get_clins(self, record_key, clins, cage_code="", duns_number=""):
        response = self._get(
            "wawf_interface.returnclinXML",
            pCage_Code=cage_code,
            pDuns_Number=duns_number,
            pUserName=self.user_name,
            pUser_Role=self.user_role,
            pRecord_key=record_key,
            pClins=clins,
        )
        # TODO: Parse XML, similar to `get_contract`
        return response
