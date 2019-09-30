import pytest

from atst.domain.csp.cloud import EnvironmentCreationException

# pylint: disable=unused-import
from tests.mock_boto3 import mock_aws, mock_boto3, AUTH_CREDENTIALS
from tests.factories import EnvironmentFactory


def test_create_environment_succeeds(mock_aws):
    environment = EnvironmentFactory.create()
    account_id = mock_aws.create_environment(
        AUTH_CREDENTIALS, environment.creator, environment
    )
    assert "account-id" == account_id


@pytest.mark.mock_boto3({"organizations.describe_create_account.failure": True})
def test_create_environment_raises_x_when_account_creation_fails(mock_aws):
    environment = EnvironmentFactory.create()
    with pytest.raises(EnvironmentCreationException):
        mock_aws.create_environment(AUTH_CREDENTIALS, environment.creator, environment)
