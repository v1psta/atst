import pytest
from uuid import uuid4

from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.projects import Projects
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.exceptions import NotFoundError

from tests.factories import RequestFactory, UserFactory


def test_update_environment_roles():
    owner = UserFactory.create()
    developer_data = {
        "dod_id": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@mail.com",
        "workspace_role": "developer",
    }

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_user = Workspaces.create_member(owner, workspace, developer_data)
    project = Projects.create(
        owner, workspace, "my test project", "It's mine.", ["dev", "staging", "prod"]
    )

    dev_env = project.environments[0]
    staging_env = project.environments[1]
    Environments.add_member(dev_env, workspace_user.user, "devops")
    Environments.add_member(staging_env, workspace_user.user, "developer")

    new_ids_and_roles = [
        {"id": dev_env.id, "role": "billing_admin"},
        {"id": staging_env.id, "role": "developer"},
    ]

    Environments.update_environment_role(owner, new_ids_and_roles, workspace_user)
    new_dev_env_role = EnvironmentRoles.get(workspace_user.user.id, dev_env.id)
    staging_env_role = EnvironmentRoles.get(workspace_user.user.id, staging_env.id)

    assert new_dev_env_role.role == "billing_admin"
    assert staging_env_role.role == "developer"
