from flask import url_for

from tests.factories import *


def test_accept_application_invitation(client, user_session):
    user = UserFactory.create()
    application = ApplicationFactory.create()
    app_role = ApplicationRoleFactory.create(application=application, user=user)
    invite = ApplicationInvitationFactory.create(
        role=app_role, user=user, inviter=application.portfolio.owner
    )

    user_session(user)
    response = client.get(url_for("applications.accept_invitation", token=invite.token))

    assert response.status_code == 302
    expected_location = url_for(
        "portfolios.show_portfolio",
        portfolio_id=application.portfolio_id,
        _external=True,
    )
    assert response.location == expected_location
