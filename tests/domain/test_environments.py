from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.portfolio_roles import PortfolioRoles

from tests.factories import ApplicationFactory, UserFactory, PortfolioFactory


def test_create_environments():
    application = ApplicationFactory.create()
    environments = Environments.create_many(application, ["Staging", "Production"])
    for env in environments:
        assert env.cloud_id is not None


def test_create_environment_role_creates_cloud_id(session):
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=owner,
        members=[{"user": developer, "role_name": "developer"}],
        applications=[
            {"name": "application1", "environments": [{"name": "application1 prod"}]}
        ],
    )

    env = portfolio.applications[0].environments[0]
    new_role = [{"id": env.id, "role": "developer"}]

    portfolio_role = portfolio.members[0]
    assert not portfolio_role.user.cloud_id
    assert Environments.update_environment_roles(
        owner, portfolio, portfolio_role, new_role
    )

    assert portfolio_role.user.cloud_id is not None


def test_update_environment_roles():
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=owner,
        members=[{"user": developer, "role_name": "developer"}],
        applications=[
            {
                "name": "application1",
                "environments": [
                    {
                        "name": "application1 dev",
                        "members": [{"user": developer, "role_name": "devlops"}],
                    },
                    {
                        "name": "application1 staging",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {"name": "application1 prod"},
                ],
            }
        ],
    )

    dev_env = portfolio.applications[0].environments[0]
    staging_env = portfolio.applications[0].environments[1]
    new_ids_and_roles = [
        {"id": dev_env.id, "role": "billing_admin"},
        {"id": staging_env.id, "role": "developer"},
    ]

    portfolio_role = portfolio.members[0]
    assert Environments.update_environment_roles(
        owner, portfolio, portfolio_role, new_ids_and_roles
    )
    new_dev_env_role = EnvironmentRoles.get(portfolio_role.user.id, dev_env.id)
    staging_env_role = EnvironmentRoles.get(portfolio_role.user.id, staging_env.id)

    assert new_dev_env_role.role == "billing_admin"
    assert staging_env_role.role == "developer"


def test_remove_environment_role():
    owner = UserFactory.create()
    developer = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        members=[{"user": developer, "role_name": "developer"}],
        applications=[
            {
                "name": "application1",
                "environments": [
                    {
                        "name": "application1 dev",
                        "members": [{"user": developer, "role_name": "devops"}],
                    },
                    {
                        "name": "application1 staging",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {
                        "name": "application1 uat",
                        "members": [
                            {"user": developer, "role_name": "financial_auditor"}
                        ],
                    },
                    {"name": "application1 prod"},
                ],
            }
        ],
    )

    application = portfolio.applications[0]
    now_ba = application.environments[0].id
    now_none = application.environments[1].id
    still_fa = application.environments[2].id

    new_environment_roles = [
        {"id": now_ba, "role": "billing_auditor"},
        {"id": now_none, "role": None},
    ]

    portfolio_role = PortfolioRoles.get(portfolio.id, developer.id)
    assert Environments.update_environment_roles(
        owner, portfolio, portfolio_role, new_environment_roles
    )

    assert portfolio_role.num_environment_roles == 2
    assert EnvironmentRoles.get(developer.id, now_ba).role == "billing_auditor"
    assert EnvironmentRoles.get(developer.id, now_none) is None
    assert EnvironmentRoles.get(developer.id, still_fa).role == "financial_auditor"


def test_no_update_to_environment_roles():
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=owner,
        members=[{"user": developer, "role_name": "developer"}],
        applications=[
            {
                "name": "application1",
                "environments": [
                    {
                        "name": "application1 dev",
                        "members": [{"user": developer, "role_name": "devops"}],
                    }
                ],
            }
        ],
    )

    dev_env = portfolio.applications[0].environments[0]
    new_ids_and_roles = [{"id": dev_env.id, "role": "devops"}]

    portfolio_role = PortfolioRoles.get(portfolio.id, developer.id)
    assert not Environments.update_environment_roles(
        owner, portfolio, portfolio_role, new_ids_and_roles
    )


def test_get_scoped_environments(db):
    developer = UserFactory.create()
    portfolio = PortfolioFactory.create(
        members=[{"user": developer, "role_name": "developer"}],
        applications=[
            {
                "name": "application1",
                "environments": [
                    {
                        "name": "application1 dev",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {"name": "application1 staging"},
                    {"name": "application1 prod"},
                ],
            },
            {
                "name": "application2",
                "environments": [
                    {"name": "application2 dev"},
                    {
                        "name": "application2 staging",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {"name": "application2 prod"},
                ],
            },
        ],
    )

    application1_envs = Environments.for_user(developer, portfolio.applications[0])
    assert [env.name for env in application1_envs] == ["application1 dev"]

    application2_envs = Environments.for_user(developer, portfolio.applications[1])
    assert [env.name for env in application2_envs] == ["application2 staging"]
