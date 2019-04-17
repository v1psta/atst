from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from . import BaseDomainClass
from atst.domain.environments import Environments
from atst.domain.exceptions import NotFoundError
from atst.models.application import Application
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole


class Applications(BaseDomainClass):
    model = Application
    resource_name = "application"

    @classmethod
    def create(cls, portfolio, name, description, environment_names):
        application = Application(
            portfolio=portfolio, name=name, description=description
        )
        db.session.add(application)

        Environments.create_many(application, environment_names)

        db.session.commit()
        return application

    @classmethod
    def for_user(self, user, portfolio):
        return (
            db.session.query(Application)
            .join(Environment)
            .join(EnvironmentRole)
            .filter(Application.portfolio_id == portfolio.id)
            .filter(EnvironmentRole.user_id == user.id)
            .all()
        )

    @classmethod
    def get_all(cls, portfolio):
        try:
            applications = (
                db.session.query(Application).filter_by(portfolio_id=portfolio.id).all()
            )
        except NoResultFound:
            raise NotFoundError("applications")

        return applications

    @classmethod
    def update(cls, application, new_data):
        if "name" in new_data:
            application.name = new_data["name"]
        if "description" in new_data:
            application.description = new_data["description"]

        db.session.add(application)
        db.session.commit()

        return application

    @classmethod
    def delete(cls, application):
        for env in application.environments:
            Environments.delete(env)

        application.deleted = True

        for role in application.roles:
            role.deleted = True
            db.session.add(role)

        db.session.add(application)
        db.session.commit()
