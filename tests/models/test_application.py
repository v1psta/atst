from tests.factories import ApplicationFactory, ApplicationRoleFactory


def test_application_num_users():
    application = ApplicationFactory.create(
        environments=[{"name": "dev"}, {"name": "staging"}, {"name": "prod"}]
    )
    assert application.num_users == 0

    ApplicationRoleFactory.create(application=application)
    assert application.num_users == 1
