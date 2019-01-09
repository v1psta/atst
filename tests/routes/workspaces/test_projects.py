from flask import url_for

from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceRoleFactory,
    EnvironmentRoleFactory,
    EnvironmentFactory,
    ProjectFactory,
)

from atst.domain.projects import Projects
from atst.domain.workspaces import Workspaces
from atst.domain.roles import Roles
from atst.models.workspace_role import Status as WorkspaceRoleStatus


def test_user_with_permission_has_budget_report_link(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/reports"'.format(workspace.id).encode() in response.data
    )


def test_user_without_permission_has_no_budget_report_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(
        user, workspace, "developer", status=WorkspaceRoleStatus.ACTIVE
    )
    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/reports"'.format(workspace.id).encode()
        not in response.data
    )


def test_user_with_permission_has_activity_log_link(client, user_session):
    workspace = WorkspaceFactory.create()
    ccpo = UserFactory.from_atat_role("ccpo")
    admin = UserFactory.create()
    WorkspaceRoleFactory.create(
        workspace=workspace,
        user=admin,
        role=Roles.get("admin"),
        status=WorkspaceRoleStatus.ACTIVE,
    )

    user_session(workspace.owner)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/activity"'.format(workspace.id).encode() in response.data
    )

    # logs out previous user before creating a new session
    user_session(admin)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/activity"'.format(workspace.id).encode() in response.data
    )

    user_session(ccpo)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/activity"'.format(workspace.id).encode() in response.data
    )


def test_user_without_permission_has_no_activity_log_link(client, user_session):
    workspace = WorkspaceFactory.create()
    developer = UserFactory.create()
    WorkspaceRoleFactory.create(
        workspace=workspace,
        user=developer,
        role=Roles.get("developer"),
        status=WorkspaceRoleStatus.ACTIVE,
    )

    user_session(developer)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/activity"'.format(workspace.id).encode()
        not in response.data
    )


def test_user_with_permission_has_add_project_link(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/projects/new"'.format(workspace.id).encode()
        in response.data
    )


def test_user_without_permission_has_no_add_project_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/projects/new"'.format(workspace.id).encode()
        not in response.data
    )


def test_view_edit_project(client, user_session):
    workspace = WorkspaceFactory.create()
    project = Projects.create(
        workspace.owner,
        workspace,
        "Snazzy Project",
        "A new project for me and my friends",
        {"env1", "env2"},
    )
    user_session(workspace.owner)
    response = client.get(
        "/workspaces/{}/projects/{}/edit".format(workspace.id, project.id)
    )
    assert response.status_code == 200


def test_user_with_permission_can_update_project(client, user_session):
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create(
        owner=owner,
        projects=[
            {
                "name": "Awesome Project",
                "description": "It's really awesome!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    project = workspace.projects[0]
    user_session(owner)
    response = client.post(
        url_for(
            "workspaces.update_project",
            workspace_id=workspace.id,
            project_id=project.id,
        ),
        data={"name": "Really Cool Project", "description": "A very cool project."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert project.name == "Really Cool Project"
    assert project.description == "A very cool project."


def test_user_without_permission_cannot_update_project(client, user_session):
    dev = UserFactory.create()
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create(
        owner=owner,
        members=[{"user": dev, "role_name": "developer"}],
        projects=[
            {
                "name": "Great Project",
                "description": "Cool stuff happening here!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    project = workspace.projects[0]
    user_session(dev)
    response = client.post(
        url_for(
            "workspaces.update_project",
            workspace_id=workspace.id,
            project_id=project.id,
        ),
        data={"name": "New Name", "description": "A new description."},
        follow_redirects=True,
    )

    assert response.status_code == 404
    assert project.name == "Great Project"
    assert project.description == "Cool stuff happening here!"


def create_environment(user):
    workspace = WorkspaceFactory.create()
    workspace_role = WorkspaceRoleFactory.create(workspace=workspace, user=user)
    project = ProjectFactory.create(workspace=workspace)
    return EnvironmentFactory.create(project=project, name="new environment!")


def test_environment_access_with_env_role(client, user_session):
    user = UserFactory.create()
    environment = create_environment(user)
    env_role = EnvironmentRoleFactory.create(
        user=user, environment=environment, role="developer"
    )
    user_session(user)
    response = client.get(
        url_for(
            "workspaces.access_environment",
            workspace_id=environment.workspace.id,
            environment_id=environment.id,
        )
    )
    assert response.status_code == 302
    assert "csp-environment-access" in response.location


def test_environment_access_with_no_role(client, user_session):
    user = UserFactory.create()
    environment = create_environment(user)
    user_session(user)
    response = client.get(
        url_for(
            "workspaces.access_environment",
            workspace_id=environment.workspace.id,
            environment_id=environment.id,
        )
    )
    assert response.status_code == 404
