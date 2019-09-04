from typing import Dict
from uuid import uuid4

from atst.models.environment_role import CSPRole
from atst.models.user import User
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole


class GeneralCSPException(Exception):
    pass


class CloudProviderInterface:
    def create_environment(
        self, auth_credentials: Dict, user: User, environment: Environment
    ) -> str:
        """Create a new environment in the CSP.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            user -- ATAT user authorizing the environment creation
            environment -- ATAT Environment model

        Returns:
            string: ID of created environment
        """
        raise NotImplementedError()

    def create_atat_admin_user(
        self, auth_credentials: Dict, csp_environment_id: str
    ) -> Dict:
        """Creates a new, programmatic user in the CSP. Grants this user full permissions to administer
        the CSP.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_environment_id -- ID of the CSP Environment the admin user should be created in

        Returns:
            object: Object representing new remote admin user, including credentials
            Something like:
            {
                "user_id": string,
                "credentials": dict, # structure TBD based on csp
            }
        """
        raise NotImplementedError()

    def create_environment_baseline(
        self, auth_credentials: Dict, csp_environment_id: str
    ) -> Dict:
        """Provision the necessary baseline entities (such as roles) in the given environment

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_environment_id -- ID of the CSP Environment to provision roles against.

        Returns:
            dict: Returns dict that associates the resource identities with their ATAT representations.
        """
        raise NotImplementedError()

    def create_or_update_user(
        self, auth_credentials: Dict, user_info: EnvironmentRole, csp_role_id: str
    ) -> str:
        """Creates a user or updates an existing user's role.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            user_info -- instance of EnvironmentRole containing user data
                         if it has a csp_user_id it will try to update that user
            csp_role_id -- The id of the role the user should be given in the CSP

        Returns:
            string: Returns the interal csp_user_id of the created/updated user account
        """
        raise NotImplementedError()

    def suspend_user(self, auth_credentials: Dict, csp_user_id: str) -> bool:
        """Revoke all privileges for a user. Used to prevent user access while a full
        delete is being processed.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_user_id -- CSP internal user identifier

        Returns:
            bool -- True on success
        """
        raise NotImplementedError()

    def delete_user(self, auth_credentials: Dict, csp_user_id: str) -> bool:
        """Given the csp-internal id for a user, initiate user deletion.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_user_id -- CSP internal user identifier

        Returns:
            bool -- True on success

        Raises:
            TBDException: Some part of user deletion failed
        """
        raise NotImplementedError()

    def get_calculator_url(self) -> str:
        """Returns the calculator url for the CSP.
        This will likely be a static property elsewhere once a CSP is chosen.
        """
        raise NotImplementedError()

    def get_environment_login_url(self, environment) -> str:
        """Returns the login url for a given environment
        This may move to be a computed property on the Environment domain object
        """
        raise NotImplementedError()


class MockCloudProvider(CloudProviderInterface):

    # TODO: All of these constants
    AUTH_EXCEPTION = GeneralCSPException("Authentication failure.")
    NETWORK_EXCEPTION = GeneralCSPException("Network failure.")

    NETWORK_FAILURE_PCT = 7
    ENV_CREATE_FAILURE_PCT = 12
    ATAT_ADMIN_CREATE_FAILURE_PCT = 12

    def __init__(self, with_delay=True, with_failure=True):
        from time import sleep
        import random

        self._with_delay = with_delay
        self._with_failure = with_failure
        self._sleep = sleep
        self._random = random

    def create_environment(self, auth_credentials, user, environment):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_throw(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_throw(
            self.ENV_CREATE_FAILURE_PCT,
            GeneralCSPException("Could not create environment."),
        )

        return self._id()

    def create_atat_admin_user(self, auth_credentials, csp_environment_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_throw(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_throw(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            GeneralCSPException("Could not create admin user."),
        )

        return {"id": self._id(), "credentials": {}}

    def create_environment_baseline(self, auth_credentials, csp_environment_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_throw(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_throw(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            GeneralCSPException("Could not create environment baseline."),
        )

        return {
            CSPRole.BASIC_ACCESS: self._id(),
            CSPRole.NETWORK_ADMIN: self._id(),
            CSPRole.BUSINESS_READ: self._id(),
            CSPRole.TECHNICAL_READ: self._id(),
        }

    def create_or_update_user(self, auth_credentials, user_info, csp_role_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_throw(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_throw(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            GeneralCSPException("Could not create user."),
        )

        return {"id": self._id()}

    def suspend_user(self, auth_credentials, csp_user_id):
        return self._maybe(12)

    def delete_user(self, auth_credentials, csp_user_id):
        return self._maybe(12)

    def get_calculator_url(self):
        return "https://www.rackspace.com/en-us/calculator"

    def get_environment_login_url(self, environment):
        """Returns the login url for a given environment
        """
        return "https://www.mycloud.com/my-env-login"

    def _id(self):
        return uuid4().hex

    def _delay(self, min_secs, max_secs):
        if self._with_delay:
            duration = self._random.randrange(min_secs, max_secs)
            self._sleep(duration)

    def _maybe(self, pct):
        return not self._with_failure or self._random.randrange(0, 100) < pct

    def _maybe_throw(self, pct, exc):
        if self._with_failure and self._maybe(pct):
            raise exc

    @property
    def _auth_credentials(self):
        return {"username": "mock-cloud", "pass": "shh"}

    def _authorize(self, credentials):
        self._delay(1, 5)
        if credentials != self._auth_credentials:
            raise self.AUTH_EXCEPTION
