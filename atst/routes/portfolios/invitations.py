from flask import g, redirect, url_for, render_template, request as http_request

from .blueprint import portfolios_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.invitations import PortfolioInvitations
from atst.domain.portfolios import Portfolios
from atst.models import Permissions
from atst.jobs import send_mail
from atst.utils.flash import formatted_flash as flash
from atst.utils.localization import translate
import atst.forms.portfolio_member as member_forms


def send_portfolio_invitation(invitee_email, inviter_name, token):
    body = render_template(
        "emails/portfolio/invitation.txt", owner=inviter_name, token=token
    )
    send_mail.delay(
        [invitee_email],
        translate("email.portfolio_invite", {"inviter_name": inviter_name}),
        body,
    )


@portfolios_bp.route("/portfolios/invitations/<portfolio_token>", methods=["GET"])
def accept_invitation(portfolio_token):
    invite = PortfolioInvitations.accept(g.current_user, portfolio_token)

    return redirect(
        url_for("applications.portfolio_applications", portfolio_id=invite.portfolio.id)
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/invitations/<portfolio_token>/revoke", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="revoke invitation")
def revoke_invitation(portfolio_id, portfolio_token):
    PortfolioInvitations.revoke(portfolio_token)

    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio_id,
            _anchor="portfolio-members",
            fragment="portfolio-members",
        )
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/invitations/<portfolio_token>/resend", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="resend invitation")
def resend_invitation(portfolio_id, portfolio_token):
    invite = PortfolioInvitations.resend(g.current_user, portfolio_token)
    send_portfolio_invitation(
        invitee_email=invite.email,
        inviter_name=g.current_user.full_name,
        token=invite.token,
    )
    flash("resend_portfolio_invitation", user_name=invite.user_name)
    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio_id,
            fragment="portfolio-members",
            _anchor="portfolio-members",
        )
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/members/new", methods=["POST"])
@user_can(Permissions.CREATE_PORTFOLIO_USERS, message="create new portfolio member")
def invite_member(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    form = member_forms.NewForm(http_request.form)

    if form.validate():
        try:
            invite = Portfolios.invite(portfolio, g.current_user, form.data)
            send_portfolio_invitation(
                invitee_email=invite.email,
                inviter_name=g.current_user.full_name,
                token=invite.token,
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
