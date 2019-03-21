import re

from flask import render_template, request as http_request, g, redirect, url_for

from . import portfolios_bp
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.applications import Applications
from atst.domain.portfolios import Portfolios
from atst.domain.portfolio_roles import PortfolioRoles, MEMBER_STATUS_CHOICES
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.services.invitation import Invitation as InvitationService
import atst.forms.portfolio_member as member_forms
from atst.forms.data import ENVIRONMENT_ROLES, ENV_ROLE_MODAL_DESCRIPTION
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions

from atst.utils.flash import formatted_flash as flash


def serialize_portfolio_role(portfolio_role):
    return {
        "name": portfolio_role.user_name,
        "status": portfolio_role.display_status,
        "id": portfolio_role.user_id,
        "role": "admin",
        "num_env": portfolio_role.num_environment_roles,
        "edit_link": url_for(
            "portfolios.view_member",
            portfolio_id=portfolio_role.portfolio_id,
            member_id=portfolio_role.user_id,
        ),
    }


@portfolios_bp.route("/portfolios/<portfolio_id>/members")
@user_can(Permissions.VIEW_PORTFOLIO_USERS, message="view portfolio members")
def portfolio_members(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    members_list = [serialize_portfolio_role(k) for k in portfolio.members]

    return render_template(
        "portfolios/members/index.html",
        portfolio=portfolio,
        status_choices=MEMBER_STATUS_CHOICES,
        members=members_list,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/<application_id>/members")
@user_can(Permissions.VIEW_APPLICATION_MEMBER, message="view application members")
def application_members(portfolio_id, application_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    application = Applications.get(application_id)
    # TODO: this should show only members that have env roles in this application
    members_list = [serialize_portfolio_role(k) for k in portfolio.members]

    return render_template(
        "portfolios/applications/members.html",
        portfolio=portfolio,
        application=application,
        members=members_list,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/members/new")
@user_can(
    Permissions.CREATE_PORTFOLIO_USERS, message="view create new portfolio member form"
)
def new_member(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    form = member_forms.NewForm()
    return render_template(
        "portfolios/members/new.html", portfolio=portfolio, form=form
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/members/new", methods=["POST"])
@user_can(Permissions.CREATE_PORTFOLIO_USERS, message="create new portfolio member")
def create_member(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    form = member_forms.NewForm(http_request.form)

    if form.validate():
        try:
            member = Portfolios.create_member(portfolio, form.data)
            invite_service = InvitationService(
                g.current_user, member, form.data.get("email")
            )
            invite_service.invite()

            flash("new_portfolio_member", new_member=member, portfolio=portfolio)

            return redirect(
                url_for("portfolios.portfolio_members", portfolio_id=portfolio.id)
            )
        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        return render_template(
            "portfolios/members/new.html", portfolio=portfolio, form=form
        )


@portfolios_bp.route("/portfolios/<portfolio_id>/members/<member_id>/member_edit")
@user_can(Permissions.VIEW_PORTFOLIO_USERS, message="view portfolio member")
def view_member(portfolio_id, member_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    member = PortfolioRoles.get(portfolio_id, member_id)
    applications = Applications.get_all(portfolio)
    form = member_forms.EditForm(portfolio_role="admin")
    editable = g.current_user == member.user
    can_revoke_access = Portfolios.can_revoke_access_for(portfolio, member)

    if member.has_dod_id_error:
        flash("portfolio_member_dod_id_error")

    return render_template(
        "portfolios/members/edit.html",
        portfolio=portfolio,
        member=member,
        applications=applications,
        form=form,
        choices=ENVIRONMENT_ROLES,
        env_role_modal_description=ENV_ROLE_MODAL_DESCRIPTION,
        EnvironmentRoles=EnvironmentRoles,
        editable=editable,
        can_revoke_access=can_revoke_access,
    )


# TODO: check if member_id is consistent with other routes here;
# user ID vs portfolio role ID
@portfolios_bp.route(
    "/portfolios/<portfolio_id>/members/<member_id>/member_edit", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="update portfolio member")
def update_member(portfolio_id, member_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    member = PortfolioRoles.get(portfolio_id, member_id)

    ids_and_roles = []
    form_dict = http_request.form.to_dict()
    for entry in form_dict:
        if re.match("env_", entry):
            env_id = entry[4:]
            env_role = form_dict[entry] or None
            ids_and_roles.append({"id": env_id, "role": env_role})

    form = member_forms.EditForm(http_request.form)
    if form.validate():
        member = Portfolios.update_member(member, form.data["permission_sets"])
        updated_roles = Environments.update_environment_roles(member, ids_and_roles)
        if updated_roles:
            flash("environment_access_changed")

        return redirect(
            url_for("portfolios.portfolio_members", portfolio_id=portfolio.id)
        )
    else:
        return render_template(
            "portfolios/members/edit.html",
            form=form,
            portfolio=portfolio,
            member=member,
        )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/members/<member_id>/revoke_access", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="revoke portfolio access")
def revoke_access(portfolio_id, member_id):
    revoked_role = Portfolios.revoke_access(portfolio_id, member_id)
    flash("revoked_portfolio_access", member_name=revoked_role.user.full_name)
    return redirect(url_for("portfolios.portfolio_members", portfolio_id=portfolio_id))
