# Add root application dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import ctypes
import sqlalchemy
from sqlalchemy import event as sqlalchemy_event

from atst.database import db
from atst.app import make_config, make_app

from atst.models.audit_event import AuditEvent
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole
from atst.models.application import Application
from atst.models.role import Role
from atst.models.user import User
from atst.models.portfolio_role import PortfolioRole
from atst.models.portfolio import Portfolio
from atst.models.mixins import AuditableMixin

from atst.domain.environments import Environments
from atst.domain.exceptions import NotFoundError
from atst.domain.csp.reports import MockReportingProvider
from atst.domain.portfolios import Portfolios
from atst.domain.users import Users


dod_ids = [
    "1234567890",
    "2345678901",
    "3456789012",
    "4567890123",
    "5678901234",
    "6789012345",
    "2342342342",  # Andy
    "3453453453",  # Sally
    "4564564564",  # Betty
    "6786786786",
]


def remove_sample_data(all_users=False):
    query = db.session.query(User)
    if not all_users:
        query = query.filter(User.dod_id.in_(dod_ids))
    users = query.all()

    delete_listeners = [
        k
        for k in sqlalchemy_event.registry._key_to_collection
        if k[1] == "after_delete"
    ]
    for listener in delete_listeners:
        [class_id, identifier, _] = listener
        model = ctypes.cast(class_id, ctypes.py_object).value
        sqlalchemy_event.remove(model, identifier, AuditableMixin.audit_delete)

    for user in users:
        all_portfolios = Portfolios.for_user(user)
        portfolios = [p for p in all_portfolios if p.owner == user]

        ws_audit = (
            db.session.query(AuditEvent)
            .filter(AuditEvent.portfolio_id.in_([w.id for w in portfolios]))
            .all()
        )
        portfolio_roles = [role for portfolio in portfolios for role in portfolio.roles]
        task_orders = [to for portfolio in portfolios for to in portfolio.task_orders]
        invites = [invite for role in portfolio_roles for invite in role.invitations]
        applications = [p for portfolio in portfolios for p in portfolio.applications]
        environments = (
            db.session.query(Environment)
            .filter(Environment.application_id.in_([p.id for p in applications]))
            .all()
        )
        roles = [role for env in environments for role in env.roles]

        for set_of_things in [
            roles,
            environments,
            applications,
            invites,
            task_orders,
            portfolio_roles,
            ws_audit,
        ]:
            for thing in set_of_things:
                db.session.delete(thing)

        db.session.commit()

        query = "DELETE FROM portfolios WHERE portfolios.id = ANY(:ids);"
        db.session.connection().execute(
            sqlalchemy.text(query), ids=[w.id for w in portfolios]
        )
        db.session.commit()


if __name__ == "__main__":
    config = make_config({"DISABLE_CRL_CHECK": True, "DEBUG": False})
    app = make_app(config)
    with app.app_context():
        remove_sample_data()
