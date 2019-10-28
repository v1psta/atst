import pytest

from atst.domain.csp.cloud import EnvironmentCreationException
from atst.jobs import do_create_environment, do_create_atat_admin_user

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


def test_create_atat_admin_user_succeeds(mock_aws):
    root_user_info = mock_aws.create_atat_admin_user(
        AUTH_CREDENTIALS, "csp_environment_id"
    )
    assert {
        "id": "user-id",
        "username": "user-name",
        "resource_id": "user-arn",
        "credentials": {
            "AccessKeyId": "access-key-id",
            "SecretAccessKey": "secret-access-key",
        },
    } == root_user_info


@pytest.mark.mock_boto3({"iam.create_user.already_exists": True})
def test_create_atat_admin_when_user_already_exists(mock_aws):
    root_user_info = mock_aws.create_atat_admin_user(
        AUTH_CREDENTIALS, "csp_environment_id"
    )
    assert {
        "id": "user-id",
        "username": "user-name",
        "resource_id": "user-arn",
        "credentials": {
            "AccessKeyId": "access-key-id",
            "SecretAccessKey": "secret-access-key",
        },
    } == root_user_info

    iam_client = mock_aws.boto3.client("iam")
    iam_client.get_user.assert_any_call(UserName="atat")


def test_aws_provision_environment(mock_aws, session):
    environment = EnvironmentFactory.create()

    do_create_environment(mock_aws, environment_id=environment.id)
    do_create_atat_admin_user(mock_aws, environment_id=environment.id)

    session.refresh(environment)

    assert "account-id" == environment.cloud_id
    assert {
        "id": "user-id",
        "username": "user-name",
        "credentials": {
            "AccessKeyId": "access-key-id",
            "SecretAccessKey": "secret-access-key",
        },
        "resource_id": "user-arn",
    } == environment.root_user_info
    assert {
        "policies": [{"BillingReadOnly": "policy-arn"}]
    } == environment.baseline_info
