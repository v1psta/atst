import re

from flask import render_template, request as http_request, g, redirect, url_for

from . import workspaces_bp
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.projects import Projects
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_roles import WorkspaceRoles, MEMBER_STATUS_CHOICES
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.services.invitation import Invitation as InvitationService
from atst.forms.new_member import NewMemberForm
from atst.forms.edit_member import EditMemberForm
from atst.forms.data import (
    ENVIRONMENT_ROLES,
    ENV_ROLE_MODAL_DESCRIPTION,
    WORKSPACE_ROLE_DEFINITIONS,
)
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions

from atst.utils.flash import formatted_flash as flash


@workspaces_bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    workspace = Workspaces.get_with_members(g.current_user, workspace_id)
    new_member_name = http_request.args.get("newMemberName")
    new_member = next(
        filter(lambda m: m.user_name == new_member_name, workspace.members), None
    )
    members_list = [
        {
            "name": k.user_name,
            "status": k.display_status,
            "id": k.user_id,
            "role": k.role_displayname,
            "num_env": k.num_environment_roles,
            "edit_link": url_for(
                "workspaces.view_member", workspace_id=workspace.id, member_id=k.user_id
            ),
        }
        for k in workspace.members
    ]

    return render_template(
        "workspaces/members/index.html",
        workspace=workspace,
        role_choices=WORKSPACE_ROLE_DEFINITIONS,
        status_choices=MEMBER_STATUS_CHOICES,
        members=members_list,
        new_member=new_member,
    )


@workspaces_bp.route("/workspaces/<workspace_id>/members/new")
def new_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm()
    return render_template(
        "workspaces/members/new.html", workspace=workspace, form=form
    )


@workspaces_bp.route("/workspaces/<workspace_id>/members/new", methods=["POST"])
def create_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm(http_request.form)

    if form.validate():
        try:
            invite_service = InvitationService(g.current_user, workspace, form.data)
            invite_service.invite()

            flash("new_workspace_member", new_member=new_member, workspace=workspace)

            return redirect(
                url_for("workspaces.workspace_members", workspace_id=workspace.id)
            )
        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        return render_template(
            "workspaces/members/new.html", workspace=workspace, form=form
        )


@workspaces_bp.route("/workspaces/<workspace_id>/members/<member_id>/member_edit")
def view_member(workspace_id, member_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    Authorization.check_workspace_permission(
        g.current_user,
        workspace,
        Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
        "edit this workspace user",
    )
    member = WorkspaceRoles.get(workspace_id, member_id)
    projects = Projects.get_all(g.current_user, member, workspace)
    form = EditMemberForm(workspace_role=member.role_name)
    editable = g.current_user == member.user
    can_revoke_access = Workspaces.can_revoke_access_for(workspace, member)

    if member.has_dod_id_error:
        flash("workspace_member_dod_id_error")

    return render_template(
        "workspaces/members/edit.html",
        workspace=workspace,
        member=member,
        projects=projects,
        form=form,
        choices=ENVIRONMENT_ROLES,
        env_role_modal_description=ENV_ROLE_MODAL_DESCRIPTION,
        EnvironmentRoles=EnvironmentRoles,
        editable=editable,
        can_revoke_access=can_revoke_access,
    )


@workspaces_bp.route(
    "/workspaces/<workspace_id>/members/<member_id>/member_edit", methods=["POST"]
)
def update_member(workspace_id, member_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    Authorization.check_workspace_permission(
        g.current_user,
        workspace,
        Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
        "edit this workspace user",
    )
    member = WorkspaceRoles.get(workspace_id, member_id)

    ids_and_roles = []
    form_dict = http_request.form.to_dict()
    for entry in form_dict:
        if re.match("env_", entry):
            env_id = entry[4:]
            env_role = form_dict[entry] or None
            ids_and_roles.append({"id": env_id, "role": env_role})

    form = EditMemberForm(http_request.form)
    if form.validate():
        new_role_name = None
        if form.data["workspace_role"] != member.role.name:
            member = Workspaces.update_member(
                g.current_user, workspace, member, form.data["workspace_role"]
            )
            new_role_name = member.role_displayname
            flash(
                "workspace_role_updated",
                member_name=member.user_name,
                updated_role=new_role_name,
            )

        updated_roles = Environments.update_environment_roles(
            g.current_user, workspace, member, ids_and_roles
        )
        if updated_roles:
            flash("environment_access_changed")

        return redirect(
            url_for("workspaces.workspace_members", workspace_id=workspace.id)
        )
    else:
        return render_template(
            "workspaces/members/edit.html",
            form=form,
            workspace=workspace,
            member=member,
        )


@workspaces_bp.route(
    "/workspaces/<workspace_id>/members/<member_id>/revoke_access", methods=["POST"]
)
def revoke_access(workspace_id, member_id):
    revoked_role = Workspaces.revoke_access(g.current_user, workspace_id, member_id)
    flash("revoked_workspace_access", member_name=revoked_role.user.full_name)
    return redirect(url_for("workspaces.workspace_members", workspace_id=workspace_id))
