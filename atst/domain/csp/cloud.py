from typing import Dict
from uuid import uuid4
import json

from atst.models.environment_role import CSPRole
from atst.models.user import User
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole

from botocore.waiter import WaiterModel, create_waiter_with_client, WaiterError


class GeneralCSPException(Exception):
    pass


class OperationInProgressException(GeneralCSPException):
    """Throw this for instances when the CSP reports that the current entity is already
    being operated on/created/deleted/etc
    """

    def __init__(self, operation_desc):
        self.operation_desc = operation_desc

    @property
    def message(self):
        return "An operation for this entity is already in progress: {}".format(
            self.operation_desc
        )


class AuthenticationException(GeneralCSPException):
    """Throw this for instances when there is a problem with the auth credentials:
    * Missing credentials
    * Incorrect credentials
    * Other credential problems
    """

    def __init__(self, auth_error):
        self.auth_error = auth_error

    @property
    def message(self):
        return "An error occurred with authentication: {}".format(self.auth_error)


class AuthorizationException(GeneralCSPException):
    """Throw this for instances when the current credentials are not authorized
    for the current action.
    """

    def __init__(self, auth_error):
        self.auth_error = auth_error

    @property
    def message(self):
        return "An error occurred with authorization: {}".format(self.auth_error)


class ConnectionException(GeneralCSPException):
    """A general problem with the connection, timeouts or unresolved endpoints
    """

    def __init__(self, connection_error):
        self.connection_error = connection_error

    @property
    def message(self):
        return "Could not connect to cloud provider: {}".format(self.connection_error)


class UnknownServerException(GeneralCSPException):
    """An error occured on the CSP side (5xx) and we don't know why
    """

    def __init__(self, server_error):
        self.server_error = server_error

    @property
    def message(self):
        return "A server error occured: {}".format(self.server_error)


class EnvironmentCreationException(GeneralCSPException):
    """If there was an error in creating the environment
    """

    def __init__(self, env_identifier, reason):
        self.env_identifier = env_identifier
        self.reason = reason

    @property
    def message(self):
        return "The envionment {} couldn't be created: {}".format(
            self.env_identifier, self.reason
        )


class UserProvisioningException(GeneralCSPException):
    """Failed to provision a user
    """

    def __init__(self, env_identifier, user_identifier, reason):
        self.env_identifier = env_identifier
        self.user_identifier = user_identifier
        self.reason = reason

    @property
    def message(self):
        return "Failed to create user {} for environment {}: {}".format(
            self.user_identifier, self.env_identifier, self.reason
        )


class UserRemovalException(GeneralCSPException):
    """Failed to remove a user
    """

    def __init__(self, user_csp_id, reason):
        self.user_csp_id = user_csp_id
        self.reason = reason

    @property
    def message(self):
        return "Failed to suspend or delete user {}: {}".format(
            self.user_csp_id, self.reason
        )


class BaselineProvisionException(GeneralCSPException):
    """If there's any issues standing up whatever is required
    for an environment baseline
    """

    def __init__(self, env_identifier, reason):
        self.env_identifier = env_identifier
        self.reason = reason

    @property
    def message(self):
        return "Could not complete baseline provisioning for environment ({}): {}".format(
            self.env_identifier, self.reason
        )


class CloudProviderInterface:
    def root_creds() -> Dict:
        raise NotImplementedError()

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

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            EnvironmentExistsException: Environment already exists and has been created
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

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            UserProvisioningException: Problem creating the root user
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
        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            BaselineProvisionException: Specific issue occurred with some aspect of baseline setup
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

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            UserProvisioningException: User couldn't be created or modified
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

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            UserRemovalException: User couldn't be suspended
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
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            UserRemovalException: User couldn't be removed
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
    AUTHENTICATION_EXCEPTION = AuthenticationException("Authentication failure.")
    AUTHORIZATION_EXCEPTION = AuthorizationException("Not authorized.")
    NETWORK_EXCEPTION = ConnectionException("Network failure.")
    SERVER_EXCEPTION = UnknownServerException("Not our fault.")

    SERVER_FAILURE_PCT = 1
    NETWORK_FAILURE_PCT = 7
    ENV_CREATE_FAILURE_PCT = 12
    ATAT_ADMIN_CREATE_FAILURE_PCT = 12
    UNAUTHORIZED_RATE = 2

    def __init__(self, config, with_delay=True, with_failure=True):
        from time import sleep
        import random

        self._with_delay = with_delay
        self._with_failure = with_failure
        self._sleep = sleep
        self._random = random

    def root_creds(self):
        return self._auth_credentials

    def create_environment(self, auth_credentials, user, environment):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ENV_CREATE_FAILURE_PCT,
            EnvironmentCreationException(
                environment.id, "Could not create environment."
            ),
        )
        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)

        return self._id()

    def create_atat_admin_user(self, auth_credentials, csp_environment_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            UserProvisioningException(
                csp_environment_id, "atat_admin", "Could not create admin user."
            ),
        )

        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)

        return {"id": self._id(), "credentials": self._auth_credentials}

    def create_environment_baseline(self, auth_credentials, csp_environment_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            BaselineProvisionException(
                csp_environment_id, "Could not create environment baseline."
            ),
        )

        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)
        return {
            CSPRole.BASIC_ACCESS.value: self._id(),
            CSPRole.NETWORK_ADMIN.value: self._id(),
            CSPRole.BUSINESS_READ.value: self._id(),
            CSPRole.TECHNICAL_READ.value: self._id(),
        }

    def create_or_update_user(self, auth_credentials, user_info, csp_role_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            UserProvisioningException(
                user_info.environment.id,
                user_info.application_role.user_id,
                "Could not create user.",
            ),
        )

        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)
        return self._id()

    def suspend_user(self, auth_credentials, csp_user_id):
        self._authorize(auth_credentials)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)

        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            UserRemovalException(csp_user_id, "Could not suspend user."),
        )

        return self._maybe(12)

    def delete_user(self, auth_credentials, csp_user_id):
        self._authorize(auth_credentials)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)

        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            UserRemovalException(csp_user_id, "Could not delete user."),
        )

        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)
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

    def _maybe_raise(self, pct, exc):
        if self._with_failure and self._maybe(pct):
            raise exc

    @property
    def _auth_credentials(self):
        return {"username": "mock-cloud", "pass": "shh"}

    def _authorize(self, credentials):
        self._delay(1, 5)
        if credentials != self._auth_credentials:
            raise self.AUTHENTICATION_EXCEPTION


class AWSCloudProvider(CloudProviderInterface):
    # These are standins that will be replaced with "real" policies once we know what they are.
    BASELINE_POLICIES = [
        {
            "name": "BillingReadOnly",
            "path": "/atat/billing-read-only/",
            "document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "VisualEditor0",
                        "Effect": "Allow",
                        "Action": [
                            "aws-portal:ViewPaymentMethods",
                            "aws-portal:ViewAccount",
                            "aws-portal:ViewBilling",
                            "aws-portal:ViewUsage",
                        ],
                        "Resource": "*",
                    }
                ],
            },
            "description": "View billing information.",
        }
    ]

    def __init__(self, config, boto3=None):
        self.config = config

        self.access_key_id = config["AWS_ACCESS_KEY_ID"]
        self.secret_key = config["AWS_SECRET_KEY"]
        self.region_name = config["AWS_REGION_NAME"]

        # TODO: Discuss these values.
        self.role_access_org_name = "OrganizationAccountAccessRole"
        self.root_account_username = "atat"
        self.root_account_policy_name = "OrganizationAccountAccessRole"

        if boto3:
            self.boto3 = boto3
        else:
            import boto3

            self.boto3 = boto3

    def root_creds(self):
        return {"AccessKeyId": self.access_key_id, "SecretAccessKey": self.secret_key}

    def create_environment(
        self, auth_credentials: Dict, user: User, environment: Environment
    ):

        org_client = self._get_client("organizations")

        # Create an account. Requires organizations:CreateAccount permission
        account_request = org_client.create_account(
            Email=user.email, AccountName=uuid4().hex, IamUserAccessToBilling="ALLOW"
        )

        # Configuration for our CreateAccount Waiter.
        # A waiter is a boto3 helper which can be configured to poll a given status
        # endpoint until it succeeds or fails. boto3 has many built in waiters, but none
        # for the organizations service so we're building our own here.
        waiter_config = {
            "version": 2,
            "waiters": {
                "AccountCreated": {
                    "operation": "DescribeCreateAccountStatus",
                    "delay": 20,
                    "maxAttempts": 10,
                    "acceptors": [
                        {
                            "matcher": "path",
                            "expected": "SUCCEEDED",
                            "argument": "CreateAccountStatus.State",
                            "state": "success",
                        },
                        {
                            "matcher": "path",
                            "expected": "IN_PROGRESS",
                            "argument": "CreateAccountStatus.State",
                            "state": "retry",
                        },
                        {
                            "matcher": "path",
                            "expected": "FAILED",
                            "argument": "CreateAccountStatus.State",
                            "state": "failure",
                        },
                    ],
                }
            },
        }
        waiter_model = WaiterModel(waiter_config)
        account_waiter = create_waiter_with_client(
            "AccountCreated", waiter_model, org_client
        )

        try:
            # Poll until the CreateAccount request either succeeds or fails.
            account_waiter.wait(
                CreateAccountRequestId=account_request["CreateAccountStatus"]["Id"]
            )
        except WaiterError:
            # TODO: Possible failure reasons:
            # 'ACCOUNT_LIMIT_EXCEEDED'|'EMAIL_ALREADY_EXISTS'|'INVALID_ADDRESS'|'INVALID_EMAIL'|'CONCURRENT_ACCOUNT_MODIFICATION'|'INTERNAL_FAILURE'
            raise EnvironmentCreationException(
                environment.id, "Failed to create account."
            )

        # We need to re-fetch this since the Waiter throws away the success response for some reason.
        created_account_status = org_client.describe_create_account_status(
            CreateAccountRequestId=account_request["CreateAccountStatus"]["Id"]
        )
        account_id = created_account_status["CreateAccountStatus"]["AccountId"]

        return account_id

    def create_atat_admin_user(
        self, auth_credentials: Dict, csp_environment_id: str
    ) -> Dict:
        """
        Create an IAM user within a given account.
        """

        # Create a policy which allows user to assume a role within the account.
        iam_client = self._get_client("iam")
        iam_client.put_user_policy(
            UserName=self.root_account_username,
            PolicyName=f"assume-role-{self.root_account_policy_name}-{csp_environment_id}",
            PolicyDocument=self._inline_org_management_policy(csp_environment_id),
        )

        role_arn = (
            f"arn:aws:iam::{csp_environment_id}:role/{self.root_account_policy_name}"
        )
        sts_client = self._get_client("sts", credentials=auth_credentials)
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName="AssumeRoleSession1"
        )

        # From the response that contains the assumed role, get the temporary
        # credentials that can be used to make subsequent API calls
        credentials = assumed_role_object["Credentials"]

        # Use the temporary credentials that AssumeRole returns to make a new connection to IAM
        iam_client = self.boto3.client(
            "iam",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )

        # Create the user with a PermissionBoundary
        permission_boundary_arn = "arn:aws:iam::aws:policy/AlexaForBusinessDeviceSetup"
        try:
            user = iam_client.create_user(
                UserName=self.root_account_username,
                PermissionsBoundary=permission_boundary_arn,
                Tags=[{"Key": "foo", "Value": "bar"}],
            )["User"]
        except iam_client.exceptions.EntityAlreadyExistsException as _exc:
            # TODO: Find user, iterate through existing access keys and revoke them.
            user = iam_client.get_user(UserName=self.root_account_username)["User"]

        access_key = iam_client.create_access_key(UserName=self.root_account_username)[
            "AccessKey"
        ]
        credentials = {
            "AccessKeyId": access_key["AccessKeyId"],
            "SecretAccessKey": access_key["SecretAccessKey"],
        }

        # TODO: Create real policies in account.

        return {
            "id": user["UserId"],
            "username": user["UserName"],
            "resource_id": user["Arn"],
            "credentials": credentials,
        }

    def create_environment_baseline(
        self, auth_credentials: Dict, csp_environment_id: str
    ) -> Dict:
        """Provision the necessary baseline entities (such as roles) in the given environment

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_environment_id -- ID of the CSP Environment to provision roles against.

        Returns:
            dict: Returns dict that associates the resource identities with their ATAT representations.
        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            BaselineProvisionException: Specific issue occurred with some aspect of baseline setup
        """

        client = self._get_client("iam", credentials=auth_credentials)
        created_policies = []

        for policy in self.BASELINE_POLICIES:
            try:
                response = client.create_policy(
                    PolicyName=policy["name"],
                    Path=policy["path"],
                    PolicyDocument=json.dumps(policy["document"]),
                    Description=policy["description"],
                )
                created_policies.append({policy["name"]: response["Policy"]["Arn"]})
            except client.exceptions.EntityAlreadyExistsException:
                # Policy already exists. We can determine its ARN based on the account id and policy path / name.
                policy_arn = f"arn:aws:iam:{csp_environment_id}:policy{policy['path']}{policy['name']}"
                created_policies.append({policy["name"]: policy_arn})

        return {"policies": created_policies}

    def _get_client(self, service: str, credentials=None):
        """
        A helper for creating a client of a given AWS service.
        """
        credentials = credentials or {
            "AccessKeyId": self.access_key_id,
            "SecretAccessKey": self.secret_key,
        }
        return self.boto3.client(
            service,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            region_name=self.region_name,
        )

    def _inline_org_management_policy(self, account_id: str) -> Dict:
        policy_dict = json.loads(
            """
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                "Effect": "Allow",
                "Action": [
                    "sts:AssumeRole"
                ],
                "Resource": [
                    "arn:aws:iam::{}:role/{}"
                ]
                }
            ]
        }
        """
        )
        policy_dict["Statement"][0]["Resource"][0] = policy_dict["Statement"][0][
            "Resource"
        ][0].format(account_id, self.root_account_policy_name)
        return json.dumps(policy_dict)
