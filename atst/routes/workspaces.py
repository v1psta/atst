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

from atst.domain.exceptions import UnauthorizedError
from atst.domain.projects import Projects
from atst.domain.reports import Reports
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.forms.new_project import NewProjectForm
from atst.forms.new_member import NewMemberForm
from atst.forms.edit_member import EditMemberForm
from atst.forms.workspace import WorkspaceForm
from atst.forms.data import ENVIRONMENT_ROLES
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
    return render_template("workspaces/members/index.html", workspace=workspace)


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
        remaining_days = 0

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
    form = NewProjectForm(
        name=project.name,
        environment_names=[env.name for env in project.environments],
        description=project.description,
    )

    return render_template(
        "workspaces/projects/edit.html", workspace=workspace, project=project, form=form
    )


@bp.route("/workspaces/<workspace_id>/members/new")
def new_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm()
    return render_template(
        "workspaces/members/new.html", workspace=workspace, form=form
    )


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
    member = WorkspaceUsers.get(workspace_id, member_id)
    projects = Projects.get_all(g.current_user, member, workspace)
    form = EditMemberForm(workspace_role=member.role)
    return render_template(
        "workspaces/members/edit.html",
        workspace=workspace,
        member=member,
        projects=projects,
        form=form,
        choices=ENVIRONMENT_ROLES,
        EnvironmentRoles=EnvironmentRoles,
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

    ids_and_roles = []
    form_dict = http_request.form.to_dict()
    for entry in form_dict:
        if re.match("env_", entry):
            env_id = entry[4:]
            env_role = form_dict[entry]
            ids_and_roles.append({"id": env_id, "role": env_role})

    form = EditMemberForm(http_request.form)

    if form.validate():
        new_role_name = None
        if form.data["workspace_role"] != member.role:
            member = Workspaces.update_member(
                g.current_user, workspace, member, form.data["workspace_role"]
            )
            new_role_name = member.role_displayname

        Environments.update_environment_role(g.current_user, ids_and_roles, member)

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
