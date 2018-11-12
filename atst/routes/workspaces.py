import re
from datetime import date, timedelta

from flask import (
    Blueprint,
    render_template,
    request as http_request,
    g,
    redirect,
    url_for,
)

from atst.domain.exceptions import UnauthorizedError, AlreadyExistsError
from atst.domain.projects import Projects
from atst.domain.reports import Reports
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_roles import WorkspaceRoles, MEMBER_STATUSES
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.forms.project import NewProjectForm, ProjectForm
from atst.forms.new_member import NewMemberForm
from atst.forms.edit_member import EditMemberForm
from atst.forms.workspace import WorkspaceForm
from atst.forms.data import (
    ENVIRONMENT_ROLES,
    ENV_ROLE_MODAL_DESCRIPTION,
    WORKSPACE_ROLE_DEFINITIONS,
)
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.invitations import Invitations
from atst.queue import queue

bp = Blueprint("workspaces", __name__)


@bp.context_processor
def workspace():
    workspaces = Workspaces.for_user(g.current_user)
    workspace = None
    if "workspace_id" in http_request.view_args:
        try:
            workspace = Workspaces.get(
                g.current_user, http_request.view_args["workspace_id"]
            )
            workspaces = [ws for ws in workspaces if not ws.id == workspace.id]
        except UnauthorizedError:
            pass

    def user_can(permission):
        if workspace:
            return Authorization.has_workspace_permission(
                g.current_user, workspace, permission
            )
        return False

    return {
        "workspace": workspace,
        "workspaces": workspaces,
        "permissions": Permissions,
        "user_can": user_can,
    }


@bp.route("/workspaces")
def workspaces():
    workspaces = Workspaces.for_user(g.current_user)
    return render_template("workspaces/index.html", page=5, workspaces=workspaces)


@bp.route("/workspaces/<workspace_id>/edit")
def workspace(workspace_id):
    workspace = Workspaces.get_for_update_information(g.current_user, workspace_id)
    form = WorkspaceForm(data={"name": workspace.name})
    return render_template("workspaces/edit.html", form=form, workspace=workspace)


@bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspaces/projects/index.html", workspace=workspace)


@bp.route("/workspaces/<workspace_id>/edit", methods=["POST"])
def edit_workspace(workspace_id):
    workspace = Workspaces.get_for_update_information(g.current_user, workspace_id)
    form = WorkspaceForm(http_request.form)
    if form.validate():
        Workspaces.update(workspace, form.data)
        return redirect(
            url_for("workspaces.workspace_projects", workspace_id=workspace.id)
        )
    else:
        return render_template("workspaces/edit.html", form=form, workspace=workspace)


@bp.route("/workspaces/<workspace_id>")
def show_workspace(workspace_id):
    return redirect(url_for("workspaces.workspace_projects", workspace_id=workspace_id))


@bp.route("/workspaces/<workspace_id>/members")
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
        status_choices=MEMBER_STATUSES,
        members=members_list,
        new_member=new_member,
    )


@bp.route("/workspaces/<workspace_id>/reports")
def workspace_reports(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    Authorization.check_workspace_permission(
        g.current_user,
        workspace,
        Permissions.VIEW_USAGE_DOLLARS,
        "view workspace reports",
    )

    today = date.today()
    month = http_request.args.get("month", today.month)
    year = http_request.args.get("year", today.year)
    current_month = date(int(year), int(month), 15)
    prev_month = current_month - timedelta(days=28)
    two_months_ago = prev_month - timedelta(days=28)

    expiration_date = workspace.request.task_order.expiration_date
    if expiration_date:
        remaining_difference = expiration_date - today
        remaining_days = remaining_difference.days
    else:
        remaining_days = None

    return render_template(
        "workspaces/reports/index.html",
        cumulative_budget=Reports.cumulative_budget(workspace),
        workspace_totals=Reports.workspace_totals(workspace),
        monthly_totals=Reports.monthly_totals(workspace),
        jedi_request=workspace.request,
        task_order=workspace.request.task_order,
        current_month=current_month,
        prev_month=prev_month,
        two_months_ago=two_months_ago,
        expiration_date=expiration_date,
        remaining_days=remaining_days,
    )


@bp.route("/workspaces/<workspace_id>/projects/new")
def new_project(workspace_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    form = NewProjectForm()
    return render_template(
        "workspaces/projects/new.html", workspace=workspace, form=form
    )


@bp.route("/workspaces/<workspace_id>/projects/new", methods=["POST"])
def create_project(workspace_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    form = NewProjectForm(http_request.form)

    if form.validate():
        project_data = form.data
        Projects.create(
            g.current_user,
            workspace,
            project_data["name"],
            project_data["description"],
            project_data["environment_names"],
        )
        return redirect(
            url_for("workspaces.workspace_projects", workspace_id=workspace.id)
        )
    else:
        return render_template(
            "workspaces/projects/new.html", workspace=workspace, form=form
        )


@bp.route("/workspaces/<workspace_id>/projects/<project_id>/edit")
def edit_project(workspace_id, project_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    project = Projects.get(g.current_user, workspace, project_id)
    form = ProjectForm(name=project.name, description=project.description)

    return render_template(
        "workspaces/projects/edit.html", workspace=workspace, project=project, form=form
    )


@bp.route("/workspaces/<workspace_id>/projects/<project_id>/edit", methods=["POST"])
def update_project(workspace_id, project_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    project = Projects.get(g.current_user, workspace, project_id)
    form = ProjectForm(http_request.form)
    if form.validate():
        project_data = form.data
        Projects.update(g.current_user, workspace, project, project_data)

        return redirect(
            url_for("workspaces.workspace_projects", workspace_id=workspace.id)
        )
    else:
        return render_template(
            "workspaces/projects/edit.html",
            workspace=workspace,
            project=project,
            form=form,
        )


@bp.route("/workspaces/<workspace_id>/members/new")
def new_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm()
    return render_template(
        "workspaces/members/new.html", workspace=workspace, form=form
    )


def send_invite_email(owner_name, token, new_member_email):
    body = render_template("emails/invitation.txt", owner=owner_name, token=token)
    queue.send_mail(
        [new_member_email],
        "{} has invited you to a JEDI Cloud Workspace".format(owner_name),
        body,
    )


@bp.route("/workspaces/<workspace_id>/members/new", methods=["POST"])
def create_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm(http_request.form)
    user = g.current_user

    if form.validate():
        try:
            new_member = Workspaces.create_member(user, workspace, form.data)
            invite = Invitations.create(user, new_member)
            send_invite_email(
                g.current_user.full_name, invite.token, new_member.user.email
            )

            return redirect(
                url_for(
                    "workspaces.workspace_members",
                    workspace_id=workspace.id,
                    newMemberName=new_member.user_name,
                )
            )
        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        return render_template(
            "workspaces/members/new.html", workspace=workspace, form=form
        )


@bp.route("/workspaces/<workspace_id>/members/<member_id>/member_edit")
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
    )


@bp.route(
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
        if form.data["workspace_role"] != member.role:
            member = Workspaces.update_member(
                g.current_user, workspace, member, form.data["workspace_role"]
            )
            new_role_name = member.role_displayname

        Environments.update_environment_roles(
            g.current_user, workspace, member, ids_and_roles
        )

        return redirect(
            url_for(
                "workspaces.workspace_members",
                workspace_id=workspace.id,
                memberName=member.user_name,
                updatedRole=new_role_name,
            )
        )
    else:
        return render_template(
            "workspaces/members/edit.html",
            form=form,
            workspace=workspace,
            member=member,
        )


@bp.route("/workspaces/invitations/<token>", methods=["GET"])
def accept_invitation(token):
    invite = Invitations.accept(g.current_user, token)

    return redirect(
        url_for("workspaces.show_workspace", workspace_id=invite.workspace.id)
    )


@bp.route("/workspaces/<workspace_id>/invitations/<token>/revoke", methods=["POST"])
def revoke_invitation(workspace_id, token):
    workspace = Workspaces.get_for_update_member(g.current_user, workspace_id)
    Invitations.revoke(token)

    return redirect(url_for("workspaces.workspace_members", workspace_id=workspace.id))


@bp.route("/workspaces/<workspace_id>/invitations/<token>/resend", methods=["POST"])
def resend_invitation(workspace_id, token):
    invite = Invitations.resend(g.current_user, workspace_id, token)
    send_invite_email(g.current_user.full_name, invite.token, invite.user_email)
    return redirect(url_for("workspaces.workspace_members", workspace_id=workspace_id))
