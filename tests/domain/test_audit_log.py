import pytest

from atst.domain.audit_log import AuditLog
from atst.domain.exceptions import UnauthorizedError
from atst.domain.roles import Roles
from atst.models.workspace_role import Status as WorkspaceRoleStatus
from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceRoleFactory,
    ProjectFactory,
)


@pytest.fixture(scope="function")
def ccpo():
    return UserFactory.from_atat_role("ccpo")


@pytest.fixture(scope="function")
def developer():
    return UserFactory.from_atat_role("default")


def test_non_admin_cannot_view_audit_log(developer):
    with pytest.raises(UnauthorizedError):
        AuditLog.get_all_events(developer)


def test_ccpo_can_view_audit_log(ccpo):
    events = AuditLog.get_all_events(ccpo)
    assert len(events) > 0


def test_paginate_audit_log(ccpo):
    user = UserFactory.create()
    for _ in range(100):
        AuditLog.log_system_event(user, action="create")

    events = AuditLog.get_all_events(ccpo, pagination_opts={"per_page": 25, "page": 2})
    assert len(events) == 25


def test_ccpo_can_view_ws_audit_log(ccpo):
    workspace = WorkspaceFactory.create()
    events = AuditLog.get_workspace_events(ccpo, workspace)
    assert len(events) > 0


def test_ws_admin_can_view_ws_audit_log():
    workspace = WorkspaceFactory.create()
    admin = UserFactory.create()
    WorkspaceRoleFactory.create(
        workspace=workspace,
        user=admin,
        role=Roles.get("admin"),
        status=WorkspaceRoleStatus.ACTIVE,
    )
    events = AuditLog.get_workspace_events(admin, workspace)
    assert len(events) > 0


def test_ws_owner_can_view_ws_audit_log():
    workspace = WorkspaceFactory.create()
    events = AuditLog.get_workspace_events(workspace.owner, workspace)
    assert len(events) > 0


def test_other_users_cannot_view_ws_audit_log():
    with pytest.raises(UnauthorizedError):
        workspace = WorkspaceFactory.create()
        dev = UserFactory.create()
        WorkspaceRoleFactory.create(
            workspace=workspace,
            user=dev,
            role=Roles.get("developer"),
            status=WorkspaceRoleStatus.ACTIVE,
        )
        AuditLog.get_workspace_events(dev, workspace)


def test_paginate_ws_audit_log():
    workspace = WorkspaceFactory.create()
    project = ProjectFactory.create(workspace=workspace)
    for _ in range(100):
        AuditLog.log_system_event(
            resource=project, action="create", workspace=workspace
        )

    events = AuditLog.get_workspace_events(
        workspace.owner, workspace, pagination_opts={"per_page": 25, "page": 2}
    )
    assert len(events) == 25


def test_ws_audit_log_only_includes_current_ws_events():
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create(owner=owner)
    other_workspace = WorkspaceFactory.create(owner=owner)
    # Add some audit events
    project_1 = ProjectFactory.create(workspace=workspace)
    project_2 = ProjectFactory.create(workspace=other_workspace)

    events = AuditLog.get_workspace_events(workspace.owner, workspace)
    for event in events:
        assert event.workspace_id == workspace.id or event.resource_id == workspace.id
        assert (
            not event.workspace_id == other_workspace.id
            or event.resource_id == other_workspace.id
        )
