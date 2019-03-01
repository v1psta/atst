import os
import datetime
import pytest
import alembic.config
import alembic.command
from logging.config import dictConfig
from werkzeug.datastructures import FileStorage
from tempfile import TemporaryDirectory
from collections import OrderedDict

from atst.app import make_app, make_config
from atst.database import db as _db
from atst.queue import queue as atst_queue
import tests.factories as factories
from tests.mocks import PDF_FILENAME, PDF_FILENAME2

dictConfig({"version": 1, "handlers": {"wsgi": {"class": "logging.NullHandler"}}})


@pytest.fixture(scope="session")
def app(request):
    upload_dir = TemporaryDirectory()

    config = make_config()
    config.update(
        {"STORAGE_CONTAINER": upload_dir.name, "CRL_STORAGE_PROVIDER": "LOCAL"}
    )

    _app = make_app(config)

    ctx = _app.app_context()
    ctx.push()

    yield _app

    upload_dir.cleanup()

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
    def __init__(self, data=OrderedDict(), errors=(), raw_data=None):
        self._fields = data
        self.errors = list(errors)


class DummyField(object):
    def __init__(self, data=None, errors=(), raw_data=None, name=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data
        self.name = name


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
            lambda *args: user or factories.UserFactory.create(),
        )

    return set_user_session


@pytest.fixture
def pdf_upload():
    with open(PDF_FILENAME, "rb") as fp:
        yield FileStorage(fp, content_type="application/pdf")


@pytest.fixture
def pdf_upload2():
    with open(PDF_FILENAME2, "rb") as fp:
        yield FileStorage(fp, content_type="application/pdf")


@pytest.fixture
def extended_financial_verification_data(pdf_upload):
    return {
        "funding_type": "RDTE",
        "funding_type_other": "other",
        "expiration_date": "1/1/{}".format(datetime.date.today().year + 1),
        "clin_0001": "50000",
        "clin_0003": "13000",
        "clin_1001": "30000",
        "clin_1003": "7000",
        "clin_2001": "30000",
        "clin_2003": "7000",
        "legacy_task_order": pdf_upload,
    }


@pytest.fixture(scope="function", autouse=True)
def queue():
    yield atst_queue
    atst_queue.get_queue().empty()
