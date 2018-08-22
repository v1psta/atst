from atst.domain.projects import Projects
from tests.factories import WorkspaceFactory


def test_create_project_with_multiple_environments():
    workspace = WorkspaceFactory.create()
    project = Projects.create(workspace, "My Test Project", "Test", ["dev", "prod"])

    assert project.workspace == workspace
    assert project.name == "My Test Project"
    assert project.description == "Test"
    assert [e.name for e in project.environments] == ["dev", "prod"]
