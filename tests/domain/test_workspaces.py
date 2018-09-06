import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError, UnauthorizedError
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers

from tests.factories import WorkspaceFactory, RequestFactory, UserFactory


def test_can_create_workspace():
    request = RequestFactory.create()
    workspace = Workspaces.create(request, name="frugal-whale")
    assert workspace.name == "frugal-whale"
    assert workspace.request == request


def test_default_workspace_name_is_request_id():
    request = RequestFactory.create()
    workspace = Workspaces.create(request)
    assert workspace.name == str(request.id)


def test_get_nonexistent_workspace_raises():
    with pytest.raises(NotFoundError):
        Workspaces.get(UserFactory.build(), uuid4())


def test_can_get_workspace_by_request():
    workspace = WorkspaceFactory.create()
    found = Workspaces.get_by_request(workspace.request)
    assert workspace == found


def test_creating_workspace_adds_owner():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    workspace = Workspaces.create(request)
    assert workspace.roles[0].user == user


def test_workspace_has_timestamps():
    request = RequestFactory.create()
    workspace = Workspaces.create(request)
    assert workspace.time_created == workspace.time_updated


def test_workspaces_get_ensures_user_is_in_workspace():
    owner = UserFactory.create()
    outside_user = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))

    workspace_ = Workspaces.get(owner, workspace.id)
    assert workspace_ == workspace

    with pytest.raises(UnauthorizedError):
        Workspaces.get(outside_user, workspace.id)


def test_workspaces_get_many_with_no_workspaces():
    workspaces = Workspaces.get_many(UserFactory.build())
    assert workspaces == []


def test_workspaces_get_many_returns_a_users_workspaces():
    user = UserFactory.create()
    users_workspace = Workspaces.create(RequestFactory.create(creator=user))

    # random workspace
    Workspaces.create(RequestFactory.create())

    assert Workspaces.get_many(user) == [users_workspace]


def test_get_for_update_allows_owner():
    owner = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    Workspaces.get_for_update(owner, workspace.id)


def test_get_for_update_blocks_developer():
    owner = UserFactory.create()
    developer = UserFactory.create()

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    WorkspaceUsers.add(developer, workspace.id, "developer")

    with pytest.raises(UnauthorizedError):
        Workspaces.get_for_update(developer, workspace.id)


def test_can_create_workspace_user():
    owner = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))

    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "workspace_role": "developer",
        "dod_id": "1234567890",
    }

    new_member = Workspaces.create_member(owner, workspace, user_data)
    assert new_member.workspace == workspace


def test_need_permission_to_create_workspace_user():
    workspace = Workspaces.create(request=RequestFactory.create())
    random_user = UserFactory.create()

    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "workspace_role": "developer",
        "dod_id": "1234567890",
    }

    with pytest.raises(UnauthorizedError):
        Workspaces.create_member(random_user, workspace, user_data)


def test_update_workspace_user_role():
    owner = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "workspace_role": "developer",
        "dod_id": "1234567890",
    }
    member = Workspaces.create_member(owner, workspace, user_data)
    role_name = "admin"

    updated_member = Workspaces.update_member(owner, workspace, member, role_name)
    assert updated_member.workspace == workspace
    assert updated_member.role == role_name


def test_need_permission_to_update_workspace_user_role():
    owner = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    random_user = UserFactory.create()
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "workspace_role": "developer",
        "dod_id": "1234567890",
    }
    member = Workspaces.create_member(owner, workspace, user_data)
    role_name = "developer"

    with pytest.raises(UnauthorizedError):
        Workspaces.update_member(random_user, workspace, member, role_name)


def test_owner_can_view_workspace_members():
    owner = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace = Workspaces.get_with_members(owner, workspace.id)

    assert workspace


def test_ccpo_can_view_workspace_members():
    workspace = Workspaces.create(RequestFactory.create(creator=UserFactory.create()))
    ccpo = UserFactory.from_atat_role("ccpo")
    workspace = Workspaces.get_with_members(ccpo, workspace.id)

    assert workspace
