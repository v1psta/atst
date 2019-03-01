# Add root application dir to the python path
import os
import sys
from datetime import datetime, timedelta, date

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atst.database import db
from atst.app import make_config, make_app
from atst.domain.users import Users
from atst.domain.portfolios import Portfolios
from atst.domain.applications import Applications
from atst.domain.portfolio_roles import PortfolioRoles
from atst.models.invitation import Status as InvitationStatus
from atst.domain.exceptions import AlreadyExistsError
from tests.factories import (
    InvitationFactory,
    TaskOrderFactory,
    random_future_date,
    random_past_date,
    random_task_order_number,
)
from atst.routes.dev import _DEV_USERS as DEV_USERS
from atst.domain.csp.reports import MockReportingProvider
from atst.models.application import Application
from atst.domain.environments import Environments


PORTFOLIO_USERS = [
    {
        "first_name": "Danny",
        "last_name": "Knight",
        "email": "knight@mil.gov",
        "portfolio_role": "developer",
        "dod_id": "0000000001",
    },
    {
        "first_name": "Mario",
        "last_name": "Hudson",
        "email": "hudson@mil.gov",
        "portfolio_role": "billing_auditor",
        "dod_id": "0000000002",
    },
    {
        "first_name": "Louise",
        "last_name": "Greer",
        "email": "greer@mil.gov",
        "portfolio_role": "admin",
        "dod_id": "0000000003",
    },
]

PORTFOLIO_INVITED_USERS = [
    {
        "first_name": "Frederick",
        "last_name": "Fitzgerald",
        "email": "frederick@mil.gov",
        "portfolio_role": "developer",
        "dod_id": "0000000004",
        "status": InvitationStatus.REJECTED_WRONG_USER,
    },
    {
        "first_name": "Gina",
        "last_name": "Guzman",
        "email": "gina@mil.gov",
        "portfolio_role": "developer",
        "dod_id": "0000000005",
        "status": InvitationStatus.REJECTED_EXPIRED,
    },
    {
        "first_name": "Hector",
        "last_name": "Harper",
        "email": "hector@mil.gov",
        "portfolio_role": "developer",
        "dod_id": "0000000006",
        "status": InvitationStatus.REVOKED,
    },
    {
        "first_name": "Isabella",
        "last_name": "Ingram",
        "email": "isabella@mil.gov",
        "portfolio_role": "developer",
        "dod_id": "0000000007",
        "status": InvitationStatus.PENDING,
    },
]


def get_users():
    users = []
    for dev_user in DEV_USERS.values():
        try:
            user = Users.create(**dev_user)
        except AlreadyExistsError:
            user = Users.get_by_dod_id(dev_user["dod_id"])

        users.append(user)
    return users


def add_members_to_portfolio(portfolio, users):
    for user in users:
        for portfolio_role in PORTFOLIO_USERS:
            ws_role = Portfolios.create_member(
                portfolio.owner, portfolio, portfolio_role
            )
            db.session.refresh(ws_role)
            PortfolioRoles.enable(ws_role)

        for portfolio_role in PORTFOLIO_INVITED_USERS:
            ws_role = Portfolios.create_member(
                portfolio.owner, portfolio, portfolio_role
            )
            invitation = InvitationFactory.build(
                portfolio_role=ws_role, status=portfolio_role["status"]
            )
            db.session.add(invitation)

    db.session.commit()


def add_active_task_order(portfolio, active_exp_days=90, clin_01=None, clin_03=None):
    start = random_past_date(year_max=1, year_min=1)
    default_kwargs = {
        "start_date": start,
        "end_date": (date.today() + timedelta(days=active_exp_days)),
        "number": random_task_order_number(),
        "portfolio": portfolio,
        "clin_02": 0,
        "clin_04": 0,
    }

    if clin_01:
        default_kwargs["clin_01"] = clin_01
    if clin_03:
        default_kwargs["clin_03"] = clin_03

    task_order = TaskOrderFactory.build(**default_kwargs)
    db.session.add(task_order)
    db.session.commit()


def add_expired_task_order(portfolio):
    start = random_past_date(year_max=3, year_min=2)
    task_order = TaskOrderFactory.build(
        start_date=start,
        end_date=(start + timedelta(days=90)),
        number=random_task_order_number(),
        portfolio=portfolio,
    )
    db.session.add(task_order)
    db.session.commit()


def add_pending_task_order(portfolio):
    start_date = random_future_date(year_min=1, year_max=2)

    task_order = TaskOrderFactory.build(
        start_date=start_date,
        end_date=(start_date + timedelta(days=90)),
        number=random_task_order_number(),
        portfolio=portfolio,
    )
    db.session.add(task_order)
    db.session.commit()


def add_applications_to_portfolio(portfolio, applications):
    for application in applications:
        Applications.create(
            portfolio.owner,
            portfolio=portfolio,
            name=application["name"],
            description=application["description"],
            environment_names=application["environments"],
        )


def create_demo_portfolio(name, data):
    try:
        portfolio_owner = Users.get_or_create_by_dod_id("2345678901")  # Amanda
        # auditor = Users.get_by_dod_id("3453453453")  # Sally
    except NotFoundError:
        print(
            "Could not find demo users; will not create demo portfolio {}".format(name)
        )
        return

    portfolio = Portfolios.create(portfolio_owner, name=name)
    clin_01 = data["budget"] * 0.8
    clin_03 = data["budget"] * 0.2

    add_active_task_order(portfolio, clin_01=clin_01, clin_03=clin_03)
    add_expired_task_order(portfolio)
    add_pending_task_order(portfolio)
    add_members_to_portfolio(portfolio, users=get_users())

    for mock_application in data["applications"]:
        application = Application(
            portfolio=portfolio, name=mock_application.name, description=""
        )
        env_names = [env.name for env in mock_application.environments]
        envs = Environments.create_many(application, env_names)
        db.session.add(application)
        db.session.commit()


def seed_db():
    users = get_users()
    amanda = Users.get_by_dod_id("2345678901")
    application_info = [
        {
            "name": "First Application",
            "description": "This is our first application",
            "environments": ["dev", "staging", "prod"],
        }
    ]

    # Create Portfolios for Amanda with mocked reporting data
    create_demo_portfolio("A-Wing", MockReportingProvider.REPORT_FIXTURE_MAP["A-Wing"])
    create_demo_portfolio("B-Wing", MockReportingProvider.REPORT_FIXTURE_MAP["B-Wing"])

    # Create Portfolio for Amanda with TO that is expiring soon and does not have another TO
    unfunded_portfolio = Portfolios.create(amanda, name="TIE Interceptor")
    add_active_task_order(unfunded_portfolio, active_exp_days=20)
    add_expired_task_order(unfunded_portfolio)
    add_members_to_portfolio(unfunded_portfolio, users=users)
    add_applications_to_portfolio(unfunded_portfolio, application_info)

    # Create Portfolio for Amanda with TO that is expiring soon and has another TO
    funded_portfolio = Portfolios.create(amanda, name="TIE Fighter")
    add_active_task_order(funded_portfolio, active_exp_days=20)
    add_expired_task_order(funded_portfolio)
    add_pending_task_order(funded_portfolio)
    add_members_to_portfolio(funded_portfolio, users=users)
    add_applications_to_portfolio(funded_portfolio, application_info)

    # create a portfolio 'Y-Wing' for each user
    for user in users:
        portfolio = Portfolios.create(user, name="Y-Wing")
        add_members_to_portfolio(portfolio, users=users)
        add_active_task_order(portfolio)
        add_expired_task_order(portfolio)
        add_pending_task_order(portfolio)
        add_applications_to_portfolio(portfolio, application_info)


if __name__ == "__main__":
    config = make_config({"DISABLE_CRL_CHECK": True, "DEBUG": False})
    app = make_app(config)
    with app.app_context():
        seed_db()
