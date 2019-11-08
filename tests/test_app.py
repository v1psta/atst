import os

import pytest

from atst.app import make_crl_validator


@pytest.fixture
def replace_crl_dir_config(app):
    original = app.config.get("CRL_STORAGE_CONTAINER")

    def _replace_crl_dir_config(crl_dir):
        app.config.update({"CRL_STORAGE_CONTAINER": crl_dir})

    yield _replace_crl_dir_config

    app.config.update({"CRL_STORAGE_CONTAINER": original})


def test_make_crl_validator_creates_crl_dir(app, tmpdir, replace_crl_dir_config):
    crl_dir = tmpdir.join("new_crl_dir")
    replace_crl_dir_config(crl_dir)
    make_crl_validator(app)
    assert os.path.isdir(crl_dir)
