from uuid import uuid4

from atst.models.environment_role import CSPRole


class CloudProviderInterface:
    def create_environment(self, auth_credentials, user):
        """Create a new environment in the CSP.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            user -- ATAT user authorizing the environment creation

        Returns:
            string: ID of created environment
        """
        raise NotImplementedError()

    def create_atat_admin_user(self, auth_credentials, csp_environment_id):
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

    def create_environment_baseline(self, auth_credentials, csp_environment_id):
        """Provision the necessary baseline entities (such as roles) in the given environment

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_environment_id -- ID of the CSP Environment to provision roles against.

        Returns:
            dict: Returns dict that associates the resource identities with their ATAT representations.
        """
        raise NotImplementedError()

    def create_or_update_user(self, auth_credentials, user_info, csp_role_id):
        """Creates a user or updates an existing user's role.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            user_info -- object containing user data, if it has a csp_user_id
                         it will try to update a user with that id
            csp_role_id -- The id of the role the user should be given in the CSP

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError()

    def suspend_user(self, auth_credentials, csp_user_id):
        """Revoke all privileges for a user. Used to prevent user access while a full
        delete is being processed.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_user_id -- CSP internal user identifier

        Returns:
            bool -- True on success
        """
        raise NotImplementedError()

    def delete_user(self, auth_credentials, csp_user_id):
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

    def get_calculator_url(self):
        """Returns the calculator url for the CSP.
        This will likely be a static property elsewhere once a CSP is chosen.
        """
        raise NotImplementedError()

    def get_environment_login_url(self, environment):
        """Returns the login url for a given environment
        This may move to be a computed property on the Environment domain object
        """
        raise NotImplementedError()


class MockCloudProvider(CloudProviderInterface):
    def create_environment(self, auth_credentials, user):
        return uuid4().hex

    def create_atat_admin_user(self, auth_credentials, csp_environment_id):
        return {"id": uuid4().hex, "credentials": {}}

    def create_environment_baseline(self, auth_credentials, csp_environment_id):
        return {
            CSPRole.BASIC_ACCESS: uuid4().hex,
            CSPRole.NETWORK_ADMIN: uuid4().hex,
            CSPRole.BUSINESS_READ: uuid4().hex,
            CSPRole.TECHNICAL_READ: uuid4().hex,
        }

    def create_or_update_user(self, auth_credentials, environment_role):
        return {"id": uuid4().hex}

    def suspend_user(self, auth_credentials, csp_user_id):
        pass

    def delete_user(self, auth_credentials, csp_user_id):
        pass

    def get_calculator_url(self):
        return "https://www.rackspace.com/en-us/calculator"

    def get_environment_login_url(self, environment):
        """Returns the login url for a given environment
        """
        return "https://www.mycloud.com/my-env-login"
