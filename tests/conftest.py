import os
import pytest
import alembic.config
import alembic.command

from atst.app import make_app, make_config
from atst.database import db as _db


@pytest.fixture(scope='session')
def app(request):
    config = make_config()

    _app = make_app(config)

    ctx = _app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    return _app


def apply_migrations():
    """Applies all alembic migrations."""
    alembic_config = os.path.join(os.path.dirname(__file__), "../", "alembic.ini")
    config = alembic.config.Config(alembic_config)
    app_config = make_config()
    config.set_main_option('sqlalchemy.url', app_config["DATABASE_URI"])
    alembic.command.upgrade(config, 'head')


@pytest.fixture(scope='session')
def db(app, request):

    def teardown():
        _db.drop_all()

    _db.app = app

    apply_migrations()

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

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
