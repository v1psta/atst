from atst.domain.projects import Projects
from tests.factories import RequestFactory, UserFactory, WorkspaceFactory
from atst.domain.workspaces import Workspaces


def test_create_project_with_multiple_environments():
    request = RequestFactory.create()
    workspace = Workspaces.create_from_request(request)
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
        owner=owner, projects=[{"environments": [{"name": "dev"}, {"name": "prod"}]}]
    )
    project = Projects.get(owner, workspace, workspace.projects[0].id)

    assert len(project.environments) == 2


def test_can_only_update_name_and_description():
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create(
        owner=owner,
        projects=[
            {
                "name": "Project 1",
                "description": "a project",
                "environments": [{"name": "dev"}],
            }
        ],
    )
    project = Projects.get(owner, workspace, workspace.projects[0].id)
    env_name = project.environments[0].name
    Projects.update(
        owner,
        workspace,
        project,
        {
            "name": "New Name",
            "description": "a new project",
            "environment_name": "prod",
        },
    )

    assert project.name == "New Name"
    assert project.description == "a new project"
    assert len(project.environments) == 1
    assert project.environments[0].name == env_name
