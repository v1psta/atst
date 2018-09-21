from atst.domain.projects import Projects
from atst.domain.workspaces import Workspaces
from tests.factories import RequestFactory


def test_create_project_with_multiple_environments():
    workspace = Workspaces.create(RequestFactory.create())
    project = Projects.create(
        workspace.owner, workspace, "My Test Project", "Test", ["dev", "prod"]
    )

    assert project.workspace == workspace
    assert project.name == "My Test Project"
    assert project.description == "Test"
    assert sorted(e.name for e in project.environments) == ["dev", "prod"]
