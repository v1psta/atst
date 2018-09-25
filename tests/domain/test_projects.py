from atst.domain.projects import Projects
from tests.factories import RequestFactory, UserFactory
from atst.domain.workspaces import Workspaces


def test_create_project_with_multiple_environments():
    request = RequestFactory.create()
    workspace = Workspaces.create(request)
    project = Projects.create(
        workspace.owner, workspace, "My Test Project", "Test", ["dev", "prod"]
    )

    assert project.workspace == workspace
    assert project.name == "My Test Project"
    assert project.description == "Test"
    assert sorted(e.name for e in project.environments) == ["dev", "prod"]


def test_project_creator_has_environment_access():
    owner = UserFactory.create()
    request = RequestFactory.create(creator=owner)
    workspace = Workspaces.create(request)
    project = Projects.create(
        owner, workspace, "My Test Project", "Test", ["dev", "prod"]
    )

    environment = project.environments[0]

    assert owner in environment.users
