import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError, UnauthorizedError
from atst.domain.portfolios import Portfolios, PortfolioError
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.applications import Applications
from atst.domain.environments import Environments
from atst.domain.permission_sets import PermissionSets, PORTFOLIO_PERMISSION_SETS
from atst.models.portfolio_role import Status as PortfolioRoleStatus

from tests.factories import UserFactory, PortfolioRoleFactory, PortfolioFactory


@pytest.fixture(scope="function")
def portfolio_owner():
    return UserFactory.create()


@pytest.fixture(scope="function")
def portfolio(portfolio_owner):
    portfolio = PortfolioFactory.create(owner=portfolio_owner)
    return portfolio


def test_can_create_portfolio():
    portfolio = PortfolioFactory.create(name="frugal-whale")
    assert portfolio.name == "frugal-whale"


def test_get_nonexistent_portfolio_raises():
    with pytest.raises(NotFoundError):
        Portfolios.get(UserFactory.build(), uuid4())


def test_creating_portfolio_adds_owner(portfolio, portfolio_owner):
    assert portfolio.roles[0].user == portfolio_owner


def test_portfolio_has_timestamps(portfolio):
    assert portfolio.time_created == portfolio.time_updated


def test_portfolios_get_ensures_user_is_in_portfolio(portfolio, portfolio_owner):
    outside_user = UserFactory.create()
    with pytest.raises(UnauthorizedError):
        Portfolios.get(outside_user, portfolio.id)


def test_get_for_update_applications_allows_owner(portfolio, portfolio_owner):
    Portfolios.get_for_update_applications(portfolio_owner, portfolio.id)


def test_get_for_update_applications_blocks_developer(portfolio):
    developer = UserFactory.create()
    PortfolioRoles.add(developer, portfolio.id)

    with pytest.raises(UnauthorizedError):
        Portfolios.get_for_update_applications(developer, portfolio.id)


def test_can_create_portfolio_role(portfolio, portfolio_owner):
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "portfolio_role": "developer",
        "dod_id": "1234567890",
    }

    new_member = Portfolios.create_member(portfolio_owner, portfolio, user_data)
    assert new_member.portfolio == portfolio
    assert new_member.user.provisional


def test_can_add_existing_user_to_portfolio(portfolio, portfolio_owner):
    user = UserFactory.create()
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "portfolio_role": "developer",
        "dod_id": user.dod_id,
    }

    new_member = Portfolios.create_member(portfolio_owner, portfolio, user_data)
    assert new_member.portfolio == portfolio
    assert new_member.user.email == user.email
    assert not new_member.user.provisional


def test_need_permission_to_create_portfolio_role(portfolio, portfolio_owner):
    random_user = UserFactory.create()

    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "portfolio_role": "developer",
        "dod_id": "1234567890",
    }

    with pytest.raises(UnauthorizedError):
        Portfolios.create_member(random_user, portfolio, user_data)


def test_update_portfolio_role_role(portfolio, portfolio_owner):
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "portfolio_role": "developer",
        "dod_id": "1234567890",
    }
    PortfolioRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    member = PortfolioRoleFactory.create(portfolio=portfolio)
    permission_sets = ["edit_portfolio_funding"]

    updated_member = Portfolios.update_member(
        portfolio_owner, portfolio, member, permission_sets=permission_sets
    )
    assert updated_member.portfolio == portfolio


def test_need_permission_to_update_portfolio_role_role(portfolio, portfolio_owner):
    random_user = UserFactory.create()
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@mail.com",
        "portfolio_role": "developer",
        "dod_id": "1234567890",
    }
    member = Portfolios.create_member(portfolio_owner, portfolio, user_data)
    role_name = "developer"

    with pytest.raises(UnauthorizedError):
        Portfolios.update_member(random_user, portfolio, member, role_name)


def test_owner_can_view_portfolio_members(portfolio, portfolio_owner):
    portfolio = Portfolios.get_with_members(portfolio_owner, portfolio.id)

    assert portfolio


@pytest.mark.skip(reason="no ccpo access yet")
def test_ccpo_can_view_portfolio_members(portfolio, portfolio_owner):
    ccpo = UserFactory.from_atat_role("ccpo")
    assert Portfolios.get_with_members(ccpo, portfolio.id)


def test_random_user_cannot_view_portfolio_members(portfolio):
    developer = UserFactory.from_atat_role("developer")

    with pytest.raises(UnauthorizedError):
        portfolio = Portfolios.get_with_members(developer, portfolio.id)


@pytest.mark.skip(reason="should be reworked pending application member changes")
def test_scoped_portfolio_only_returns_a_users_applications_and_environments(
    portfolio, portfolio_owner
):
    new_application = Applications.create(
        portfolio_owner,
        portfolio,
        "My Application",
        "My application",
        ["dev", "staging", "prod"],
    )
    Applications.create(
        portfolio_owner,
        portfolio,
        "My Application 2",
        "My application 2",
        ["dev", "staging", "prod"],
    )
    developer = UserFactory.from_atat_role("developer")
    dev_environment = Environments.add_member(
        new_application.environments[0], developer, "developer"
    )

    scoped_portfolio = Portfolios.get(developer, portfolio.id)

    # Should only return the application and environment in which the user has an
    # environment role.
    assert scoped_portfolio.applications == [new_application]
    assert scoped_portfolio.applications[0].environments == [dev_environment]


def test_scoped_portfolio_returns_all_applications_for_portfolio_admin(
    portfolio, portfolio_owner
):
    for _ in range(5):
        Applications.create(
            portfolio_owner,
            portfolio,
            "My Application",
            "My application",
            ["dev", "staging", "prod"],
        )

    admin = UserFactory.from_atat_role("default")
    perm_sets = [PermissionSets.get(prms["name"]) for prms in PORTFOLIO_PERMISSION_SETS]
    PortfolioRoleFactory.create(
        user=admin, portfolio=portfolio, permission_sets=perm_sets
    )
    scoped_portfolio = Portfolios.get(admin, portfolio.id)

    assert len(scoped_portfolio.applications) == 5
    assert len(scoped_portfolio.applications[0].environments) == 3


def test_scoped_portfolio_returns_all_applications_for_portfolio_owner(
    portfolio, portfolio_owner
):
    for _ in range(5):
        Applications.create(
            portfolio_owner,
            portfolio,
            "My Application",
            "My application",
            ["dev", "staging", "prod"],
        )

    scoped_portfolio = Portfolios.get(portfolio_owner, portfolio.id)

    assert len(scoped_portfolio.applications) == 5
    assert len(scoped_portfolio.applications[0].environments) == 3


def test_for_user_returns_active_portfolios_for_user(portfolio, portfolio_owner):
    bob = UserFactory.from_atat_role("default")
    PortfolioRoleFactory.create(
        user=bob, portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE
    )
    PortfolioFactory.create()

    bobs_portfolios = Portfolios.for_user(bob)

    assert len(bobs_portfolios) == 1


def test_for_user_does_not_return_inactive_portfolios(portfolio, portfolio_owner):
    bob = UserFactory.from_atat_role("default")
    Portfolios.add_member(portfolio, bob)
    PortfolioFactory.create()
    bobs_portfolios = Portfolios.for_user(bob)

    assert len(bobs_portfolios) == 0


def test_for_user_returns_all_portfolios_for_ccpo(portfolio, portfolio_owner):
    sam = UserFactory.from_atat_role("ccpo")
    PortfolioFactory.create()

    sams_portfolios = Portfolios.for_user(sam)
    assert len(sams_portfolios) == 2


def test_get_for_update_information(portfolio, portfolio_owner):
    owner_ws = Portfolios.get_for_update_information(portfolio_owner, portfolio.id)
    assert portfolio == owner_ws

    admin = UserFactory.create()
    perm_sets = [PermissionSets.get(prms["name"]) for prms in PORTFOLIO_PERMISSION_SETS]
    PortfolioRoleFactory.create(
        user=admin, portfolio=portfolio, permission_sets=perm_sets
    )
    admin_ws = Portfolios.get_for_update_information(admin, portfolio.id)
    assert portfolio == admin_ws

    # TODO: implement ccpo roles
    # ccpo = UserFactory.from_atat_role("ccpo")
    # assert Portfolios.get_for_update_information(ccpo, portfolio.id)

    developer = UserFactory.from_atat_role("developer")
    with pytest.raises(UnauthorizedError):
        Portfolios.get_for_update_information(developer, portfolio.id)


def test_can_create_portfolios_with_matching_names():
    portfolio_name = "Great Portfolio"
    PortfolioFactory.create(name=portfolio_name)
    PortfolioFactory.create(name=portfolio_name)


def test_able_to_revoke_portfolio_access_for_active_member():
    portfolio = PortfolioFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE
    )
    Portfolios.revoke_access(portfolio.owner, portfolio.id, portfolio_role.id)
    assert Portfolios.for_user(portfolio_role.user) == []


def test_can_revoke_access():
    portfolio = PortfolioFactory.create()
    owner_role = portfolio.roles[0]
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE
    )

    assert Portfolios.can_revoke_access_for(portfolio, portfolio_role)
    assert not Portfolios.can_revoke_access_for(portfolio, owner_role)


def test_unable_to_revoke_owner_portfolio_access():
    portfolio = PortfolioFactory.create()
    owner_portfolio_role = portfolio.roles[0]

    with pytest.raises(PortfolioError):
        Portfolios.revoke_access(portfolio.owner, portfolio.id, owner_portfolio_role.id)


def test_disabled_members_dont_show_up(session):
    portfolio = PortfolioFactory.create()
    PortfolioRoleFactory.create(portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE)
    PortfolioRoleFactory.create(
        portfolio=portfolio, status=PortfolioRoleStatus.DISABLED
    )

    # should only return portfolio owner and ACTIVE member
    assert len(portfolio.members) == 2


def test_does_not_count_disabled_members(session):
    portfolio = PortfolioFactory.create()
    PortfolioRoleFactory.create(portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE)
    PortfolioRoleFactory.create(portfolio=portfolio)
    PortfolioRoleFactory.create(
        portfolio=portfolio, status=PortfolioRoleStatus.DISABLED
    )

    assert portfolio.user_count == 3
