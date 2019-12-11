import pytest

import transitions

from atst.domain.csp import AzureCSP


class BasePortfolioCSPDetails(object):
    current_state = "unstarted"


class AzureApplicationCSPDetails:
    acct_mgmt_group_id = "00000000-0000-4000-8000-000000000000"


class AzurePortfolioCSPDetails(BasePortfolioCSPDetails, AzureCloudInterface):
    tenant_owner_id = "00000000-0000-4000-8000-000000000000"
    billing_profile_id = "00000000-0000-4000-8000-000000000000"
    tenant_username = "my_tenant"
    tenant_password = "secret"
    tenant_email = "tenantemail"
    atat_admin_kv_key = "port1-admin-creds"

    def make_tenant():
        do_call_azure():
        if make_tenant_response.is_successful():
            self.tenant_password = fjdsklfds
            self.tenant_username = te
            self.save()

    def create_atat_admin():
        creds = self.get_root_creds()
        appclient = AppClient(creds)
        new_app_response = appclient.makeApp()
        if new_app_response.is_successful():
            KV.add("{}-admin-creds", new_app_response.client_secret)
            self.atat_admin_kv_key = "{}-admin-creds"
            self.save()

    def __init__(self, source=None, csp=None):
        if source is not None:
            pass  # hydrate from source

        if csp is not None:
            self.csp = AzureCSP().cloud
        else:
            self.csp = MockCSP().cloud

        self.machine = transitions.Machine(
            model=self,
            initial=self.current_state,
            states=PortfolioFSM.states,
            ordered_transitions=PortfolioFSM.transitions,
        )

    def next_state():
        self.csp.cloud.create_tenant()

    def can_start(self):
        import ipdb

        ipdb.set_trace()
        self.force_complete()
        return True

    def can_restart(self):
        return True

    def can_complete(self):
        import ipdb

        ipdb.set_trace()
        return False

    def can_force_complete(self):
        import ipdb

        ipdb.set_trace()
        return True

    def starting(self):
        self.current_state = self.state
        import ipdb

        ipdb.set_trace()


class PortfolioFSM(object):
    # can use on_exit as the callback to serialize fetched/updated data as well as the current
    # state that workers should resume on
    states = [{"name": "unstarted", "on_exit": "starting"}, "started", "completed"]
    transitions = [
        {
            "trigger": "start",
            "source": "unstarted",
            "dest": "started",
            "conditions": "can_start",
        },
        {
            "trigger": "complete",
            "source": "started",
            "dest": "completed",
            "conditions": "can_complete",
        },
        {
            "trigger": "reset",
            "source": "completed",
            "dest": "unstarted",
            "conditions": "can_restart",
        },
    ]


def test_which_condition_is_called():
    csp_details = PortfolioCSPDetails()

    csp_details.start()
    assert csp_details.current_state == "completed"
    assert csp_details.is_completed() == True
