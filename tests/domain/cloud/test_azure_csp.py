import pytest
from unittest.mock import Mock

from uuid import uuid4

from atst.domain.csp.cloud import EnvironmentCreationException, AzureCloudProvider
from atst.jobs import (
    do_create_environment,
    do_create_atat_admin_user,
    do_create_environment_baseline,
)

from tests.mock_azure import mock_azure, AUTH_CREDENTIALS
from tests.factories import EnvironmentFactory


def test_create_environment_succeeds(mock_azure: AzureCloudProvider):
    environment = EnvironmentFactory.create()

    subscription_id = str(uuid4())

    mock_azure.sdk.subscription.SubscriptionClient.return_value.subscription_factory.create_subscription.return_value.result.return_value.subscription_link = (
        f"subscriptions/{subscription_id}"
    )

    result = mock_azure.create_environment(
        AUTH_CREDENTIALS, environment.creator, environment
    )

    assert result == subscription_id


def test_create_atat_admin_user_succeeds(mock_azure: AzureCloudProvider):
    environment_id = str(uuid4())

    csp_user_id = str(uuid4)

    mock_azure.sdk.graphrbac.GraphRbacManagementClient.return_value.service_principals.create.return_value.object_id = (
        csp_user_id
    )

    result = mock_azure.create_atat_admin_user(AUTH_CREDENTIALS, environment_id)

    assert result.get("csp_user_id") == csp_user_id
