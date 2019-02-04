# Add root application dir to the python path
import os
import sys
from datetime import datetime, timedelta, date

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atst.database import db
from atst.app import make_config, make_app
from atst.domain.users import Users
from atst.domain.requests import Requests
from atst.domain.portfolios import Portfolios
from atst.domain.applications import Applications
from atst.domain.portfolio_roles import PortfolioRoles
from atst.models.invitation import Status as InvitationStatus
from atst.domain.exceptions import AlreadyExistsError
from tests.factories import (
    InvitationFactory,
    RequestFactory,
    TaskOrderFactory,
    random_future_date,
    random_past_date,
    random_task_order_number,
)
from atst.routes.dev import _DEV_USERS as DEV_USERS

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


def seed_db():
    users = []
    for dev_user in DEV_USERS.values():
        try:
            user = Users.create(**dev_user)
        except AlreadyExistsError:
            user = Users.get_by_dod_id(dev_user["dod_id"])

        users.append(user)

    amanda = Users.get_by_dod_id("2345678901")

    # create Portfolios for all users that have funding and are not expiring soon
    for user in users:
        portfolio = Portfolios.create(
            user, name="{}'s portfolio (not expiring)".format(user.first_name)
        )
        for portfolio_role in PORTFOLIO_USERS:
            ws_role = Portfolios.create_member(user, portfolio, portfolio_role)
            db.session.refresh(ws_role)
            PortfolioRoles.enable(ws_role)

        for portfolio_role in PORTFOLIO_INVITED_USERS:
            ws_role = Portfolios.create_member(user, portfolio, portfolio_role)
            invitation = InvitationFactory.build(
                portfolio_role=ws_role, status=portfolio_role["status"]
            )
            db.session.add(invitation)

        [old_expired_start, expired_start, expired_end] = sorted(
            [
                random_past_date(year_max=3, year_min=2),
                random_past_date(year_max=2, year_min=1),
                random_past_date(year_max=1, year_min=1),
            ]
        )
        [
            first_active_start,
            second_active_start,
            first_active_end,
            second_active_end,
        ] = sorted(
            [
                expired_end,
                random_past_date(year_max=1, year_min=1),
                random_future_date(year_min=0, year_max=1),
                random_future_date(year_min=1, year_max=1),
            ]
        )

        date_ranges = [
            (old_expired_start, expired_start),
            (expired_start, expired_end),
            (first_active_start, first_active_end),
            (second_active_start, second_active_end),
        ]
        for (start_date, end_date) in date_ranges:
            task_order = TaskOrderFactory.build(
                start_date=start_date,
                end_date=end_date,
                number=random_task_order_number(),
                portfolio=portfolio,
            )
            db.session.add(task_order)

        pending_task_order = TaskOrderFactory.build(
            start_date=None, end_date=None, number=None, portfolio=portfolio
        )
        db.session.add(pending_task_order)

        db.session.commit()

        Applications.create(
            user,
            portfolio=portfolio,
            name="First Application",
            description="This is our first application.",
            environment_names=["dev", "staging", "prod"],
        )

    # Create Portfolio for Amanda with TO that is expiring soon and does not have another TO
    unfunded_portfolio = Portfolios.create(
        amanda, name="{}'s portfolio (expiring and unfunded)".format(amanda.first_name)
    )

    [past_date_1, past_date_2, past_date_3, future_date] = sorted(
        [
            random_past_date(year_max=3, year_min=2),
            random_past_date(year_max=2, year_min=1),
            random_past_date(year_max=1, year_min=1),
            (date.today() + timedelta(days=20)),
        ]
    )

    date_ranges = [
        (past_date_1, past_date_2),
        (past_date_2, past_date_3),
        (past_date_3, future_date),
    ]
    for (start_date, end_date) in date_ranges:
        task_order = TaskOrderFactory.build(
            start_date=start_date,
            end_date=end_date,
            number=random_task_order_number(),
            portfolio=unfunded_portfolio,
        )
        db.session.add(task_order)

    db.session.commit()

    Applications.create(
        amanda,
        portfolio=unfunded_portfolio,
        name="First Application",
        description="This is our first application.",
        environment_names=["dev", "staging", "prod"],
    )

    # Create Portfolio for Amanda with TO that is expiring soon and has another TO
    funded_portfolio = Portfolios.create(
        amanda, name="{}'s portfolio (expiring and funded)".format(amanda.first_name)
    )

    [
        past_date_1,
        past_date_2,
        past_date_3,
        past_date_4,
        future_date_1,
        future_date_2,
    ] = sorted(
        [
            random_past_date(year_max=3, year_min=2),
            random_past_date(year_max=2, year_min=1),
            random_past_date(year_max=1, year_min=1),
            random_past_date(year_max=1, year_min=1),
            (date.today() + timedelta(days=20)),
            random_future_date(year_min=0, year_max=1),
        ]
    )

    date_ranges = [
        (past_date_1, past_date_2),
        (past_date_2, past_date_3),
        (past_date_3, future_date_1),
        (past_date_4, future_date_2),
    ]
    for (start_date, end_date) in date_ranges:
        task_order = TaskOrderFactory.build(
            start_date=start_date,
            end_date=end_date,
            number=random_task_order_number(),
            portfolio=funded_portfolio,
        )
        db.session.add(task_order)

    db.session.commit()

    Applications.create(
        amanda,
        portfolio=funded_portfolio,
        name="First Application",
        description="This is our first application.",
        environment_names=["dev", "staging", "prod"],
    )


if __name__ == "__main__":
    config = make_config({"DISABLE_CRL_CHECK": True})
    app = make_app(config)
    with app.app_context():
        seed_db()
