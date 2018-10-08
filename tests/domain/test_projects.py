from atst.domain.projects import Projects
from tests.factories import RequestFactory, UserFactory, WorkspaceFactory
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
    workspace = WorkspaceFactory.create(
        owner=owner,
        projects=[
            {
                "environments": [
                    {"name": "dev"},
                    {"name": "prod"}
                ]
            }
        ]
    )
    project = Projects.get(owner, workspace, workspace.projects[0].id)

    assert len(project.environments) == 2
