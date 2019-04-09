from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    EnvironmentFactory,
)


def test_application_num_users():
    application = ApplicationFactory.create(
        environments=[{"name": "dev"}, {"name": "staging"}, {"name": "prod"}]
    )
    assert application.num_users == 0

    ApplicationRoleFactory.create(application=application)
    assert application.num_users == 1


def test_application_environments_excludes_deleted():
    app = ApplicationFactory.create()
    env = EnvironmentFactory.create(application=app)
    EnvironmentFactory.create(application=app, deleted=True)
    assert len(app.environments) == 1
    assert app.environments[0].id == env.id
