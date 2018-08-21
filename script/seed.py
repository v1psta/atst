# Add root project dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atst.app import make_config, make_app
from atst.domain.users import Users
from atst.domain.requests import Requests
from atst.domain.workspaces import Workspaces
from atst.domain.exceptions import AlreadyExistsError
from tests.factories import RequestFactory
from atst.routes.dev import _DEV_USERS as DEV_USERS


def seed_db():
    users = []
    for dev_user in DEV_USERS.values():
        try:
            user = Users.create(**dev_user)
            users.append(user)
        except AlreadyExistsError:
            pass

    for user in users:
        requests = []
        for dollar_value in [1, 200, 3000, 40000, 500000, 1000000]:
            request = Requests.create(
                user, RequestFactory.build_request_body(user, dollar_value)
            )
            Requests.submit(request)
            requests.append(request)

        Workspaces.create(request[0])


if __name__ == "__main__":
    config = make_config()
    app = make_app(config)
    with app.app_context():
        seed_db()
