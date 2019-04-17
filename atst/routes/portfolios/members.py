from flask import render_template, request as http_request, g, redirect, url_for

from . import portfolios_bp
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.portfolios import Portfolios
from atst.services.invitation import Invitation as InvitationService
import atst.forms.portfolio_member as member_forms
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

        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        pass
        # TODO: flash error message

    return redirect(
        url_for(
            "portfolios.portfolio_admin",
            portfolio_id=portfolio_id,
            fragment="portfolio-members",
            _anchor="portfolio-members",
        )
    )
