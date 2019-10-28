import pytest
from unittest.mock import Mock

from atst.domain.csp.cloud import EnvironmentCreationException, AzureCloudProvider
from atst.jobs import (
    do_create_environment,
    do_create_atat_admin_user,
    do_create_environment_baseline,
)

from tests.mock_azure import mock_azure, AUTH_CREDENTIALS
from tests.factories import EnvironmentFactory


def test_create_environment_succeeds(mock_azure: AzureCloudProvider):
    print(mock_azure._get_credential_obj(mock_azure._root_creds))
