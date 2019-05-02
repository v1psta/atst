from flask import url_for

from tests.factories import PortfolioFactory, ApplicationFactory, UserFactory


def test_application_team(client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)

    user_session(portfolio.owner)

    response = client.get(url_for("applications.team", application_id=application.id))
    assert response.status_code == 200


def test_create_member(client, user_session):
    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[{"name": "Naboo"}, {"name": "Endor"}]
    )
    env = application.environments[0]

    user_session(application.portfolio.owner)

    response = client.post(
        url_for("applications.create_member", application_id=application.id),
        data={
            "user_data-first_name": user.first_name,
            "user_data-last_name": user.last_name,
            "user_data-dod_id": user.dod_id,
            "user_data-email": user.email,
            "environment_roles-0-environment_id": env.id,
            "environment_roles-0-environment_name": env.name,
            "environment_roles-0-role": "Basic Access",
            "permission_sets-perms_env_mgmt": True,
            "permission_sets-perms_team_mgmt": True,
            "permission_sets-perms_del_env": True,
        },
    )

    assert response.status_code == 302
    expected_url = url_for(
        "applications.team",
        application_id=application.id,
        fragment="application-members",
        _anchor="application-members",
        _external=True,
    )
    assert response.location == expected_url
    assert len(user.application_roles) == 1
    assert user.application_roles[0].application == application
    assert len(user.environment_roles) == 1
    assert user.environment_roles[0].environment == env
