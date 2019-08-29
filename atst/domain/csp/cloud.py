from uuid import uuid4

from atst.models.environment_role import CSPRole


class CloudProviderInterface:
    def get_auth(self, auth_credentials):
        """Validate credentials and create auth object

        Arguments:
            auth_credentials -- Object containing credentials

        Returns:
            object: An object to be passed into subsequent calls
        """
        raise NotImplementedError()

    def create_environment(self, auth, user):
        """Create a new environment in the CSP.

        Arguments:
            auth -- Object representing authorization for the CSP
            user -- ATAT user authorizing the environment creation

        Returns:
            string: ID of created environment
        """
        raise NotImplementedError()

    def create_atat_admin_user(self, auth, csp_environment_id):
        """Creates a new, programmatic user in the CSP. Grants this user full permissions to administer
        the CSP. Returns a dictionary containing user details, including user's API credentials.

        Arguments:
            auth -- Object representing authorization for the CSP
            csp_environment_id -- ID of the CSP Environment the admin user should be created in

        Returns:
            object: Object representing new remote admin user, including credentials
        """
        raise NotImplementedError()

    def create_environment_baseline(self, auth, csp_environment_id):
        """Provision the necessary baseline entities (such as roles) in the given environment

        Arguments:
            auth -- Object representing authorization for the CSP
            csp_environment_id -- ID of the CSP Environment to provision roles against.

        Returns:
            dict: Returns dict that associates the resource identities with their ATAT representations.
        """
        raise NotImplementedError()

    def create_or_update_user(self, auth, user_info, csp_role_id):
        """Creates a user or updates an existing user's role.

        Arguments:
            auth -- Object representing authorization for the CSP
            user_info -- object containing user data, if it has a csp_user_id
                         it will try to update a user with that id
            csp_role_id -- The id of the role the user should be given in the CSP

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError()

    def suspend_user(self, auth, csp_user_id):
        """Revoke all privileges for a user. Used to prevent user access while a full
        delete is being processed.

        Arguments:
            auth -- Object representing authorization for the CSP
            csp_user_id -- CSP internal user identifier

        Returns:
            None
        """
        raise NotImplementedError()

    def delete_user(self, auth, csp_user_id):
        """Given the csp-internal id for a user, initiate user deletion.

        Arguments:
            auth -- Object representing authorization for the CSP
            csp_user_id -- CSP internal user identifier

        Returns:
            None

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
    def get_auth(self, auth_credentials):
        return {}

    def create_environment(self, auth, user):
        return uuid4().hex

    def create_atat_admin_user(self, auth, csp_environment_id):
        return {"id": uuid4().hex, "credentials": {}}

    def create_environment_baseline(self, auth, csp_environment_id):
        return {
            CSPRole.BASIC_ACCESS: uuid4().hex,
            CSPRole.NETWORK_ADMIN: uuid4().hex,
            CSPRole.BUSINESS_READ: uuid4().hex,
            CSPRole.TECHNICAL_READ: uuid4().hex,
        }

    def create_or_update_user(self, auth, environment_role):
        return {"id": uuid4().hex}

    def suspend_user(self, auth, csp_user_id):
        pass

    def delete_user(self, auth, csp_user_id):
        pass

    def get_calculator_url(self):
        return "https://www.rackspace.com/en-us/calculator"

    def get_environment_login_url(self, environment):
        """Returns the login url for a given environment
        """
        return "https://www.mycloud.com/my-env-login"
