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
from atst.forms.new_member import NewMemberForm
from atst.forms.edit_member import EditMemberForm
from atst.forms.data import (
    ENVIRONMENT_ROLES,
    ENV_ROLE_MODAL_DESCRIPTION,
    PORTFOLIO_ROLE_DEFINITIONS,
)
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions

from atst.utils.flash import formatted_flash as flash


@portfolios_bp.route("/portfolios/<portfolio_id>/members")
def portfolio_members(portfolio_id):
    portfolio = Portfolios.get_with_members(g.current_user, portfolio_id)
    new_member_name = http_request.args.get("newMemberName")
    new_member = next(
        filter(lambda m: m.user_name == new_member_name, portfolio.members), None
    )
    members_list = [
        {
            "name": k.user_name,
            "status": k.display_status,
            "id": k.user_id,
            "role": k.role_displayname,
            "num_env": k.num_environment_roles,
            "edit_link": url_for(
                "portfolios.view_member", portfolio_id=portfolio.id, member_id=k.user_id
            ),
        }
        for k in portfolio.members
    ]

    return render_template(
        "portfolios/members/index.html",
        portfolio=portfolio,
        role_choices=PORTFOLIO_ROLE_DEFINITIONS,
        status_choices=MEMBER_STATUS_CHOICES,
        members=members_list,
        new_member=new_member,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/members/new")
def new_member(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    form = NewMemberForm()
    return render_template(
        "portfolios/members/new.html", portfolio=portfolio, form=form
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/members/new", methods=["POST"])
def create_member(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    form = NewMemberForm(http_request.form)

    if form.validate():
        try:
            member = Portfolios.create_member(g.current_user, portfolio, form.data)
            invite_service = InvitationService(
                g.current_user, member, form.data.get("email")
            )
            invite_service.invite()

            flash("new_portfolio_member", new_member=new_member, portfolio=portfolio)

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
def view_member(portfolio_id, member_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    Authorization.check_portfolio_permission(
        g.current_user,
        portfolio,
        Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
        "edit this portfolio user",
    )
    member = PortfolioRoles.get(portfolio_id, member_id)
    applications = Applications.get_all(g.current_user, member, portfolio)
    form = EditMemberForm(portfolio_role=member.role_name)
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


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/members/<member_id>/member_edit", methods=["POST"]
)
def update_member(portfolio_id, member_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    Authorization.check_portfolio_permission(
        g.current_user,
        portfolio,
        Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
        "edit this portfolio user",
    )
    member = PortfolioRoles.get(portfolio_id, member_id)

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
        if form.data["portfolio_role"] != member.role.name:
            member = Portfolios.update_member(
                g.current_user, portfolio, member, form.data["portfolio_role"]
            )
            new_role_name = member.role_displayname
            flash(
                "portfolio_role_updated",
                member_name=member.user_name,
                updated_role=new_role_name,
            )

        updated_roles = Environments.update_environment_roles(
            g.current_user, portfolio, member, ids_and_roles
        )
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
def revoke_access(portfolio_id, member_id):
    revoked_role = Portfolios.revoke_access(g.current_user, portfolio_id, member_id)
    flash("revoked_portfolio_access", member_name=revoked_role.user.full_name)
    return redirect(url_for("portfolios.portfolio_members", portfolio_id=portfolio_id))
