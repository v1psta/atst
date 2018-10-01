import pytest
from uuid import uuid4

from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.projects import Projects
from atst.domain.roles import Roles
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.exceptions import NotFoundError
from atst.models.environment_role import EnvironmentRole

from tests.factories import (
    RequestFactory,
    UserFactory,
    WorkspaceFactory,
    EnvironmentFactory,
    ProjectFactory,
)


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


def test_get_scoped_environments(db):
    developer = UserFactory.create()
    workspace = WorkspaceFactory.create()
    workspace_user = Workspaces.add_member(workspace, developer, "developer")
    project1 = ProjectFactory.create(workspace=workspace)
    project2 = ProjectFactory.create(workspace=workspace)
    env1 = EnvironmentFactory.create(project=project1, name="project1 dev")
    env2 = EnvironmentFactory.create(project=project1, name="project1 staging")
    env3 = EnvironmentFactory.create(project=project2, name="project2 dev")
    env4 = EnvironmentFactory.create(project=project2, name="project2 staging")
    db.session.add(EnvironmentRole(user=developer, environment=env1, role="developer"))
    db.session.add(EnvironmentRole(user=developer, environment=env4, role="developer"))
    db.session.commit()

    project1_envs = Environments.for_user(developer, project1)
    assert [env.name for env in project1_envs] == ["project1 dev"]

    project2_envs = Environments.for_user(developer, project2)
    assert [env.name for env in project2_envs] == ["project2 staging"]
