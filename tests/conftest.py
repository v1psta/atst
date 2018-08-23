import os
import pytest
import alembic.config
import alembic.command
from logging.config import dictConfig

from atst.app import make_app, make_config
from atst.database import db as _db
import tests.factories as factories

dictConfig({"version": 1, "handlers": {"wsgi": {"class": "logging.NullHandler"}}})


@pytest.fixture(scope="session")
def app(request):
    config = make_config()

    _app = make_app(config)

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


def apply_migrations():
    """Applies all alembic migrations."""
    alembic_config = os.path.join(os.path.dirname(__file__), "../", "alembic.ini")
    config = alembic.config.Config(alembic_config)
    app_config = make_config()
    config.set_main_option("sqlalchemy.url", app_config["DATABASE_URI"])
    alembic.command.upgrade(config, "head")


@pytest.fixture(scope="session")
def db(app, request):

    _db.app = app

    apply_migrations()

    yield _db

    _db.drop_all()


@pytest.fixture(scope="function", autouse=True)
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    factory_list = [
        cls
        for _name, cls in factories.__dict__.items()
        if isinstance(cls, type) and cls.__module__ == "tests.factories"
    ]
    for factory in factory_list:
        factory._meta.sqlalchemy_session = session
        factory._meta.sqlalchemy_session_persistence = "commit"

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


class DummyForm(dict):
    pass


class DummyField(object):
    def __init__(self, data=None, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data


@pytest.fixture
def dummy_form():
    return DummyForm()


@pytest.fixture
def dummy_field():
    return DummyField()


@pytest.fixture
def user_session(monkeypatch, session):
    def set_user_session(user=None):
        monkeypatch.setattr(
            "atst.domain.auth.get_current_user",
            lambda *args: user or factories.UserFactory.build(),
        )

    return set_user_session
