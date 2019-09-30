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


class MockBoto3:
    def __init__(self, config=None):
        self.config = config or {}

    def client(self, client_name, **kwargs):
        return {"organizations": mock_boto_organizations}[client_name](
            **kwargs, _config=self.config
        )


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
