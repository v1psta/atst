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


def test_workspace_owner_can_view_environments():
    owner = UserFactory.create()
    request = RequestFactory.create(creator=owner)
    workspace = Workspaces.create(request)
    _project = Projects.create(
        owner, workspace, "My Test Project", "Test", ["dev", "prod"]
    )

    project = Projects.get(owner, workspace, _project.id)

    assert len(project.environments) == 2
