# Add root project dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from sqlalchemy.orm.exc import NoResultFound
from atst.app import make_config, make_app
from atst.database import db
from atst.models import Role, Permissions
from atst.domain.roles import DEFINITIONS


def seed_roles():
    for role_info in DEFINITIONS:
        role = Role(**role_info)
        try:
            existing_role = db.session.query(Role).filter_by(name=role.name).one()
            existing_role.description = role.description
            existing_role.permissions = role.permissions
            existing_role.display_name = role.display_name
            db.session.add(existing_role)
            print("Updated existing role {}".format(existing_role.name))
        except NoResultFound:
            db.session.add(role)
            print("Added new role {}".format(role.name))

    db.session.commit()


if __name__ == "__main__":
    config = make_config()
    app = make_app(config)
    with app.app_context():
        seed_roles()
