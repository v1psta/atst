from flask import render_template, request as http_request, g, redirect, url_for

from . import portfolios_bp
from atst.domain.portfolios import Portfolios
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.permission_sets import PermissionSets
from atst.domain.users import Users
from atst.domain.audit_log import AuditLog
from atst.domain.common import Paginator
from atst.domain.exceptions import NotFoundError
from atst.forms.portfolio import PortfolioForm
import atst.forms.portfolio_member as member_forms
from atst.models.permissions import Permissions
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.utils.flash import formatted_flash as flash
from atst.domain.exceptions import UnauthorizedError


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


def get_members_data(portfolio):
    members = [serialize_member_form_data(member) for member in portfolio.members]
    for member in members:
        if member["user_id"] == portfolio.owner.id:
            ppoc = member
            members.remove(member)
    members.insert(0, ppoc)
    return members


def render_admin_page(portfolio, form=None):
    pagination_opts = Paginator.get_pagination_opts(http_request)
    audit_events = AuditLog.get_portfolio_events(portfolio, pagination_opts)
    members_data = get_members_data(portfolio)
    portfolio_form = PortfolioForm(data={"name": portfolio.name})
    member_perms_form = member_forms.MembersPermissionsForm(
        data={"members_permissions": members_data}
    )

    assign_ppoc_form = member_forms.AssignPPOCForm()
    for pf_role in portfolio.roles:
        if pf_role.user != portfolio.owner and pf_role.is_active:
            assign_ppoc_form.user_id.choices += [
                (pf_role.user.id, pf_role.user.full_name)
            ]

    return render_template(
        "portfolios/admin.html",
        form=form,
        portfolio_form=portfolio_form,
        member_perms_form=member_perms_form,
        member_form=member_forms.NewForm(),
        assign_ppoc_form=assign_ppoc_form,
        portfolio=portfolio,
        audit_events=audit_events,
        user=g.current_user,
        members_data=members_data,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/admin")
@user_can(Permissions.VIEW_PORTFOLIO_ADMIN, message="view portfolio admin page")
def admin(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    return render_admin_page(portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>/admin", methods=["POST"])
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="view portfolio admin page")
def edit_members(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    member_perms_form = member_forms.MembersPermissionsForm(http_request.form)

    if member_perms_form.validate():
        for subform in member_perms_form.members_permissions:
            user_id = subform.user_id.data
            member = Users.get(user_id=user_id)
            if member is not portfolio.owner:
                new_perm_set = subform.data["permission_sets"]
                portfolio_role = PortfolioRoles.get(portfolio.id, user_id)
                PortfolioRoles.update(portfolio_role, new_perm_set)

        flash("update_portfolio_members", portfolio=portfolio)

        return redirect(
            url_for(
                "portfolios.admin",
                portfolio_id=portfolio_id,
                fragment="portfolio-members",
                _anchor="portfolio-members",
            )
        )
    else:
        return render_admin_page(portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>/update_ppoc", methods=["POST"])
@user_can(Permissions.EDIT_PORTFOLIO_POC, message="update portfolio ppoc")
def update_ppoc(portfolio_id):
    user_id = http_request.form.get("user_id")

    portfolio = Portfolios.get(g.current_user, portfolio_id)
    new_ppoc = Users.get(user_id)

    if new_ppoc not in portfolio.users:
        raise NotFoundError("user not in portfolio")

    portfolio_role = PortfolioRoles.get(portfolio_id=portfolio_id, user_id=user_id)
    PortfolioRoles.make_ppoc(portfolio_role=portfolio_role)

    flash("primary_point_of_contact_changed", ppoc_name=new_ppoc.full_name)

    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio.id,
            fragment="primary-point-of-contact",
            _anchor="primary-point-of-contact",
        )
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_PORTFOLIO_NAME, message="edit portfolio")
def edit(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    form = PortfolioForm(http_request.form)
    if form.validate():
        Portfolios.update(portfolio, form.data)
        return redirect(
            url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
        )
    else:
        # rerender portfolio admin page
        return render_admin_page(portfolio, form)


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/members/<user_id>/delete", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="update portfolio members")
def remove_member(portfolio_id, user_id):
    if str(g.current_user.id) == user_id:
        raise UnauthorizedError(
            g.current_user, "you cant remove yourself from the portfolio"
        )

    portfolio_role = PortfolioRoles.get(portfolio_id=portfolio_id, user_id=user_id)
    # TODO: should this cascade and disable any application and environment
    # roles they might have?
    PortfolioRoles.disable(portfolio_role=portfolio_role)

    flash("portfolio_member_removed", member_name=portfolio_role.user.full_name)

    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio_id,
            _anchor="portfolio-members",
            fragment="portfolio-members",
        )
    )
