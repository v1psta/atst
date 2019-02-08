from atst.domain.environments import Environments
from tests.factories import ApplicationFactory, UserFactory


def test_application_num_users():
    application = ApplicationFactory.create(
        environments=[{"name": "dev"}, {"name": "staging"}, {"name": "prod"}]
    )
    assert application.num_users == 0

    first_env = application.environments[0]
    user1 = UserFactory()
    Environments.add_member(first_env, user1, "developer")
    assert application.num_users == 1

    second_env = application.environments[-1]
    Environments.add_member(second_env, user1, "developer")
    assert application.num_users == 1

    user2 = UserFactory()
    Environments.add_member(second_env, user2, "developer")
    assert application.num_users == 2
