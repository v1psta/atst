from atst.domain.environments import Environments
from atst.domain.workspaces import Workspaces
from atst.domain.projects import Projects
from tests.factories import RequestFactory, UserFactory


def test_add_user_to_environment():
    owner = UserFactory.create()
    developer = UserFactory.from_atat_role("developer")

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    project = Projects.create(
        workspace, "my test project", "It's mine.", ["dev", "staging", "prod"]
    )
    dev_environment = project.environments[0]

    dev_environment = Environments.add_member(owner, dev_environment, developer)
    assert developer in dev_environment.users
