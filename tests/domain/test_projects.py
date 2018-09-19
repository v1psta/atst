from atst.domain.projects import Projects
from tests.factories import RequestFactory
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
