from datetime import date, timedelta

from flask import render_template, request as http_request, g, redirect, url_for

from atst.utils.flash import formatted_flash as flash

from . import portfolios_bp
from atst.domain.reports import Reports
from atst.domain.portfolios import Portfolios
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.audit_log import AuditLog
from atst.domain.common import Paginator
from atst.forms.portfolio import PortfolioForm
import atst.forms.portfolio_member as member_forms
from atst.models.permissions import Permissions
from atst.domain.permission_sets import PermissionSets
from atst.domain.authz.decorator import user_can_access_decorator as user_can


@portfolios_bp.route("/portfolios")
def portfolios():
    portfolios = Portfolios.for_user(g.current_user)

    if portfolios:
        return render_template("portfolios/index.html", page=5, portfolios=portfolios)
    else:
        return render_template("portfolios/blank_slate.html")


def permission_str(member, edit_perm_set, view_perm_set):
    if member.has_permission_set(edit_perm_set):
        return edit_perm_set
    else:
        return view_perm_set


def serialize_member_form_data(member):
    return {
        "member": member.user.full_name,
        "user_id": member.user_id,
        "perms_app_mgmt": permission_str(
            member,
            PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
            PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        ),
        "perms_funding": permission_str(
            member,
            PermissionSets.EDIT_PORTFOLIO_FUNDING,
            PermissionSets.VIEW_PORTFOLIO_FUNDING,
        ),
        "perms_reporting": permission_str(
            member,
            PermissionSets.EDIT_PORTFOLIO_REPORTS,
            PermissionSets.VIEW_PORTFOLIO_REPORTS,
        ),
        "perms_portfolio_mgmt": permission_str(
            member,
            PermissionSets.EDIT_PORTFOLIO_ADMIN,
            PermissionSets.VIEW_PORTFOLIO_ADMIN,
        ),
    }


def render_admin_page(portfolio, form=None):
    pagination_opts = Paginator.get_pagination_opts(http_request)
    audit_events = AuditLog.get_portfolio_events(portfolio, pagination_opts)
    members_data = [serialize_member_form_data(member) for member in portfolio.members]

    portfolio_form = PortfolioForm(data={"name": portfolio.name})
    member_perms_form = member_forms.MembersPermissionsForm(
        data={"members_permissions": members_data}
    )
    return render_template(
        "portfolios/admin.html",
        form=form,
        portfolio_form=portfolio_form,
        member_perms_form=member_perms_form,
        member_form=member_forms.NewForm(),
        portfolio=portfolio,
        audit_events=audit_events,
        user=g.current_user,
        members_data=members_data,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/admin")
@user_can(Permissions.VIEW_PORTFOLIO_ADMIN, message="view portfolio admin page")
def portfolio_admin(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    return render_admin_page(portfolio)


def permission_set_has_changed(old_perm_set_names, new_perm_set_names):
    has_changed = False
    for perm_name in new_perm_set_names:
        base = perm_name[4:]
        if perm_name.split("_")[0] == "edit":
            if perm_name not in old_perm_set_names:
                has_changed = True
        elif perm_name.split("_")[0] == "view":
            edit_version = "edit" + base
            if edit_version in old_perm_set_names:
                has_changed = True
    return has_changed


@portfolios_bp.route("/portfolios/<portfolio_id>/admin", methods=["POST"])
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="view portfolio admin page")
def edit_portfolio_members(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    member_perms_form = member_forms.MembersPermissionsForm(http_request.form)
    have_any_perms_changed = False

    for subform in member_perms_form.members_permissions:
        new_perm_set = subform.data["permission_sets"]
        user_id = subform.user_id.data
        portfolio_role = PortfolioRoles.get(portfolio.id, user_id)
        old_perm_set = [perm.name for perm in portfolio_role.permission_sets]

        if permission_set_has_changed(old_perm_set, new_perm_set):
            PortfolioRoles.update(portfolio_role, new_perm_set)
            have_any_perms_changed = True

    if have_any_perms_changed:
        flash("update_portfolio_members", portfolio=portfolio)

    return redirect(
        url_for(
            "portfolios.portfolio_admin",
            portfolio_id=portfolio.id,
            fragment="portfolio-members",
            _anchor="portfolio-members",
        )
    )

    return render_admin_page(portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_PORTFOLIO_NAME, message="edit portfolio")
def edit_portfolio(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    form = PortfolioForm(http_request.form)
    if form.validate():
        Portfolios.update(portfolio, form.data)
        return redirect(
            url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
        )
    else:
        # rerender portfolio admin page
        return render_admin_page(portfolio, form)


@portfolios_bp.route("/portfolios/<portfolio_id>")
@user_can(Permissions.VIEW_PORTFOLIO, message="view portfolio")
def show_portfolio(portfolio_id):
    return redirect(
        url_for("portfolios.portfolio_applications", portfolio_id=portfolio_id)
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/reports")
@user_can(Permissions.VIEW_PORTFOLIO_REPORTS, message="view portfolio reports")
def portfolio_reports(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    today = date.today()
    month = http_request.args.get("month", today.month)
    year = http_request.args.get("year", today.year)
    current_month = date(int(year), int(month), 15)
    prev_month = current_month - timedelta(days=28)
    two_months_ago = prev_month - timedelta(days=28)

    task_order = next(
        (task_order for task_order in portfolio.task_orders if task_order.is_active),
        None,
    )
    expiration_date = task_order and task_order.end_date
    if expiration_date:
        remaining_difference = expiration_date - today
        remaining_days = remaining_difference.days
    else:
        remaining_days = None

    return render_template(
        "portfolios/reports/index.html",
        cumulative_budget=Reports.cumulative_budget(portfolio),
        portfolio_totals=Reports.portfolio_totals(portfolio),
        monthly_totals=Reports.monthly_totals(portfolio),
        task_order=task_order,
        current_month=current_month,
        prev_month=prev_month,
        two_months_ago=two_months_ago,
        expiration_date=expiration_date,
        remaining_days=remaining_days,
    )
