from datetime import date, timedelta

from flask import render_template, request as http_request, g, redirect, url_for

from . import workspaces_bp
from atst.domain.reports import Reports
from atst.domain.workspaces import Workspaces
from atst.domain.audit_log import AuditLog
from atst.domain.authz import Authorization
from atst.forms.workspace import WorkspaceForm
from atst.models.permissions import Permissions


@workspaces_bp.route("/workspaces")
def workspaces():
    workspaces = Workspaces.for_user(g.current_user)
    return render_template("workspaces/index.html", page=5, workspaces=workspaces)


@workspaces_bp.route("/workspaces/<workspace_id>/edit")
def workspace(workspace_id):
    workspace = Workspaces.get_for_update_information(g.current_user, workspace_id)
    form = WorkspaceForm(data={"name": workspace.name})
    return render_template("workspaces/edit.html", form=form, workspace=workspace)


@workspaces_bp.route("/workspaces/<workspace_id>/edit", methods=["POST"])
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


@workspaces_bp.route("/workspaces/<workspace_id>")
def show_workspace(workspace_id):
    return redirect(url_for("workspaces.workspace_projects", workspace_id=workspace_id))


@workspaces_bp.route("/workspaces/<workspace_id>/reports")
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

    expiration_date = (
        workspace.legacy_task_order and workspace.legacy_task_order.expiration_date
    )
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
        legacy_task_order=workspace.legacy_task_order,
        current_month=current_month,
        prev_month=prev_month,
        two_months_ago=two_months_ago,
        expiration_date=expiration_date,
        remaining_days=remaining_days,
    )


@workspaces_bp.route("/workspaces/<workspace_id>/activity")
def workspace_activity(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    Authorization.check_workspace_permission(
        g.current_user,
        workspace,
        # TODO: diff permission
        Permissions.VIEW_USAGE_DOLLARS,
        "view workspace reports",
    )
    audit_events = AuditLog.get_workspace_events(workspace_id)

    return render_template(
        "workspaces/activity/index.html",
        workspace_name=workspace.name,
        audit_events=audit_events,
    )
