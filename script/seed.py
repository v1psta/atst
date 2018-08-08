# Add root project dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atst.app import make_config, make_app
from atst.domain.users import Users
from atst.domain.requests import Requests
from atst.routes.dev import _DEV_USERS as DEV_USERS


def seed_db():
    users = [Users.create(**dev_user) for (_, dev_user) in DEV_USERS.items()]

    for user in users:
        [Requests.create(user, {}) for _ in range(5)]


if __name__ == "__main__":
    config = make_config()
    app = make_app(config)
    with app.app_context():
        seed_db()
