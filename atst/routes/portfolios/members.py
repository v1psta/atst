from flask import render_template, request as http_request, g, redirect, url_for

from . import portfolios_bp
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.portfolios import Portfolios
import atst.forms.portfolio_member as member_forms
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions

from atst.utils.flash import formatted_flash as flash
from atst.queue import queue


def send_portfolio_invitation(invitee_email, inviter_name, token):
    body = render_template(
        "emails/portfolio/invitation.txt", owner=inviter_name, token=token
    )
    queue.send_mail(
        [invitee_email],
        "{} has invited you to a JEDI cloud portfolio".format(inviter_name),
        body,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/members/new", methods=["POST"])
@user_can(Permissions.CREATE_PORTFOLIO_USERS, message="create new portfolio member")
def create_member(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    form = member_forms.NewForm(http_request.form)

    if form.validate():
        try:
            invite = Portfolios.invite(portfolio, g.current_user, form.update_data)
            send_portfolio_invitation(
                invite.email, g.current_user.full_name, invite.token
            )

            flash(
                "new_portfolio_member", user_name=invite.user_name, portfolio=portfolio
            )

        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        pass
        # TODO: flash error message

    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio_id,
            fragment="portfolio-members",
            _anchor="portfolio-members",
        )
    )
