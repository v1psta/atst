from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles

from tests.factories import UserFactory, SuperWorkspaceFactory


def test_update_environment_roles():
    owner = UserFactory.create()
    developer = UserFactory.from_atat_role("developer")

    workspace = SuperWorkspaceFactory.create(
        owner=owner,
        members=[{"user": developer, "role_name": "developer"}],
        projects=[
            {
                "name": "project1",
                "environments": [
                    {
                        "name": "project1 dev",
                        "members": [{"user": developer, "role_name": "devlops"}],
                    },
                    {
                        "name": "project1 staging",
                        "members": [{"user": developer, "role_name": "developer"}]
                    },
                    {"name": "project1 prod"},
                ],
            }
        ],
    )

    dev_env = workspace.projects[0].environments[0]
    staging_env = workspace.projects[0].environments[1]
    new_ids_and_roles = [
        {"id": dev_env.id, "role": "billing_admin"},
        {"id": staging_env.id, "role": "developer"},
    ]

    workspace_user = workspace.members[0]
    Environments.update_environment_role(owner, new_ids_and_roles, workspace_user)
    new_dev_env_role = EnvironmentRoles.get(workspace_user.user.id, dev_env.id)
    staging_env_role = EnvironmentRoles.get(workspace_user.user.id, staging_env.id)

    assert new_dev_env_role.role == "billing_admin"
    assert staging_env_role.role == "developer"


def test_get_scoped_environments(db):
    developer = UserFactory.create()
    workspace = SuperWorkspaceFactory.create(
        members=[{"user": developer, "role_name": "developer"}],
        projects=[
            {
                "name": "project1",
                "environments": [
                    {
                        "name": "project1 dev",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {"name": "project1 staging"},
                    {"name": "project1 prod"},
                ],
            },
            {
                "name": "project2",
                "environments": [
                    {"name": "project2 dev"},
                    {
                        "name": "project2 staging",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {"name": "project2 prod"},
                ],
            },
        ],
    )

    project1_envs = Environments.for_user(developer, workspace.projects[0])
    assert [env.name for env in project1_envs] == ["project1 dev"]

    project2_envs = Environments.for_user(developer, workspace.projects[1])
    assert [env.name for env in project2_envs] == ["project2 staging"]
