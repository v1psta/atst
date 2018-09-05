from flask import (
    Blueprint,
    render_template,
    request as http_request,
    g,
    redirect,
    url_for,
)

from atst.domain.exceptions import UnauthorizedError
from atst.domain.projects import Projects
from atst.domain.reports import Reports
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers
from atst.forms.new_project import NewProjectForm
from atst.forms.new_member import NewMemberForm
from atst.forms.edit_member import EditMemberForm
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions

bp = Blueprint("workspaces", __name__)


@bp.context_processor
def workspace():
    workspace = None
    if "workspace_id" in http_request.view_args:
        try:
            workspace = Workspaces.get(
                g.current_user, http_request.view_args["workspace_id"]
            )
        except UnauthorizedError:
            pass

    def user_can(permission):
        if workspace:
            return Authorization.has_workspace_permission(
                g.current_user, workspace, permission
            )
        return False

    return {"workspace": workspace, "permissions": Permissions, "user_can": user_can}


@bp.route("/workspaces")
def workspaces():
    workspaces = Workspaces.get_many(g.current_user)
    return render_template("workspaces.html", page=5, workspaces=workspaces)


@bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspace_projects.html", workspace=workspace)


@bp.route("/workspaces/<workspace_id>")
def show_workspace(workspace_id):
    return redirect(url_for("workspaces.workspace_projects", workspace_id=workspace_id))


@bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspace_members.html", workspace=workspace)


@bp.route("/workspaces/<workspace_id>/reports")
def workspace_reports(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    if not Authorization.has_workspace_permission(
        g.current_user, workspace, Permissions.VIEW_USAGE_DOLLARS
    ):
        raise UnauthorizedError(g.current_user, "view workspace reports")

    return render_template(
        "workspace_reports.html",
        workspace_totals=Reports.workspace_totals(workspace),
        monthly_totals=Reports.monthly_totals(workspace),
    )


@bp.route("/workspaces/<workspace_id>/projects/new")
def new_project(workspace_id):
    workspace = Workspaces.get_for_update(g.current_user, workspace_id)
    form = NewProjectForm()
    return render_template("workspace_project_new.html", workspace=workspace, form=form)


@bp.route("/workspaces/<workspace_id>/projects/new", methods=["POST"])
def update_project(workspace_id):
    workspace = Workspaces.get_for_update(g.current_user, workspace_id)
    form = NewProjectForm(http_request.form)

    if form.validate():
        project_data = form.data
        Projects.create(
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
            "workspace_project_new.html", workspace=workspace, form=form
        )


@bp.route("/workspaces/<workspace_id>/members/new")
def new_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm()
    return render_template("member_new.html", workspace=workspace, form=form)


@bp.route("/workspaces/<workspace_id>/members/new", methods=["POST"])
def create_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm(http_request.form)

    if form.validate():
        new_member = Workspaces.create_member(g.current_user, workspace, form.data)
        return redirect(
            url_for(
                "workspaces.workspace_members",
                workspace_id=workspace.id,
                newMemberName=new_member.user_name,
            )
        )
    else:
        return render_template("member_new.html", workspace=workspace, form=form)


@bp.route("/workspaces/<workspace_id>/members/<member_id>/member_edit")
def view_member(workspace_id, member_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    Authorization.check_workspace_permission(
        g.current_user,
        workspace,
        Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
        "edit this workspace user",
    )
    member = WorkspaceUsers.get(workspace_id, member_id)
    form = EditMemberForm(workspace_role=member.role)
    return render_template(
        "member_edit.html", form=form, workspace=workspace, member=member
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
    member = WorkspaceUsers.get(workspace_id, member_id)
    form = EditMemberForm(http_request.form)

    if form.validate():
        role = None
        if form.data["workspace_role"] != member.role:
            role = form.data["workspace_role"]
            Workspaces.update_member(g.current_user, workspace, member, role)

        return redirect(
            url_for(
                "workspaces.workspace_members",
                workspace_id=workspace.id,
                memberName=member.user_name,
                updatedRole=role,
            )
        )
    else:
        return render_template(
            "member_edit.html", form=form, workspace=workspace, member=member
        )
