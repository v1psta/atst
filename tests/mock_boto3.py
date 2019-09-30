import pytest
from unittest.mock import Mock

from atst.domain.csp.cloud import AWSCloudProvider


AWS_CONFIG = {
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_KEY": "",
    "AWS_REGION_NAME": "us-fake-1",
}
AUTH_CREDENTIALS = {
    "aws_access_key_id": AWS_CONFIG["AWS_ACCESS_KEY_ID"],
    "aws_secret_access_key": AWS_CONFIG["AWS_SECRET_KEY"],
}


def mock_boto_organizations(_config=None, **kwargs):
    describe_create_account_status = (
        "SUCCEEDED"
        if _config.get("organizations.describe_create_account.failure", False) == False
        else "FAILED"
    )

    import boto3

    mock = Mock(wraps=boto3.client("organizations", **kwargs))

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html#Organizations.Client.create_account
    mock.create_account = Mock(
        return_value={
            "CreateAccountStatus": {
                "Id": "create-account-status-id",
                "AccountName": "account-name",
                "AccountId": "account-id",
                "State": "SUCCEEDED",
            }
        }
    )

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html#Organizations.Client.describe_create_account_status
    mock.describe_create_account_status = Mock(
        return_value={
            "CreateAccountStatus": {
                "Id": "create-account-status-id",
                "AccountName": "account-name",
                "AccountId": "account-id",
                "State": describe_create_account_status,
            }
        }
    )
    return mock


def mock_boto_iam(_config=None, **kwargs):
    user_already_exists = _config.get("iam.create_user.already_exists", False)
    policy_already_exists = _config.get("iam.create_policy.already_exists", False)

    def _raise_entity_already_exists(**kwargs):
        raise real_iam_client.exceptions.EntityAlreadyExistsException(
            {"Error": {}}, "operation-name"
        )

    import boto3

    real_iam_client = boto3.client("iam", **kwargs)
    mock = Mock(wraps=real_iam_client)
    mock.exceptions.EntityAlreadyExistsException = (
        real_iam_client.exceptions.EntityAlreadyExistsException
    )

    mock.put_user_policy = Mock(return_value={"ResponseMetadata": {}})

    if user_already_exists:
        mock.create_user = Mock(side_effect=_raise_entity_already_exists)
    else:
        mock.create_user = Mock(
            return_value={
                "User": {
                    "UserId": "user-id",
                    "Arn": "user-arn",
                    "UserName": "user-name",
                }
            }
        )

    mock.get_user = Mock(
        return_value={
            "User": {"UserId": "user-id", "Arn": "user-arn", "UserName": "user-name"}
        }
    )

    mock.create_access_key = Mock(
        return_value={
            "AccessKey": {
                "AccessKeyId": "access-key-id",
                "SecretAccessKey": "secret-access-key",
            }
        }
    )

    if policy_already_exists:
        mock.create_policy = Mock(side_effect=_raise_entity_already_exists)
    else:
        mock.create_policy = Mock(return_value={"Policy": {"Arn": "policy-arn"}})

    return mock


def mock_boto_sts(_config=None, **kwargs):
    import boto3

    mock = Mock(wraps=boto3.client("sts", **kwargs))
    mock.assume_role = Mock(
        return_value={
            "Credentials": {
                "AccessKeyId": "access-key-id",
                "SecretAccessKey": "secret-access-key",
                "SessionToken": "session-token",
            }
        }
    )

    return mock


class MockBoto3:
    CLIENTS = {
        "organizations": mock_boto_organizations,
        "iam": mock_boto_iam,
        "sts": mock_boto_sts,
    }

    def __init__(self, config=None):
        self.config = config or {}
        self.client_instances = {}

    def client(self, client_name, **kwargs):
        """
        Return a new mock client for the given `client_name`, either by
        retrieving it from the `client_instances` cache or by instantiating
        it for the first time.

        Params should be the same ones you'd pass to `boto3.client`.
        """

        if client_name in self.client_instances:
            return self.client_instances[client_name]

        try:
            client_fn = self.CLIENTS[client_name]
            client_instance = client_fn(**kwargs, _config=self.config)
            self.client_instances[client_name] = client_instance
            return client_instance
        except KeyError:
            raise ValueError(f"MockBoto3: {client_name} client is not yet implemented.")


@pytest.fixture(scope="function")
def mock_boto3(request):
    marks = request.node.get_closest_marker("mock_boto3")
    if marks:
        mock_config = marks.args[0] if len(marks.args) else {}
    else:
        mock_config = {}
    return MockBoto3(mock_config)


@pytest.fixture(scope="function")
def mock_aws(mock_boto3):
    return AWSCloudProvider(AWS_CONFIG, boto3=mock_boto3)
