import yaml
import os
from functools import lru_cache
from flask import current_app as app
from atst.utils import getattr_path

ENV = os.getenv("FLASK_ENV", "dev")


class LocalizationInvalidKeyError(Exception):
    def __init__(self, key, variables):
        self.key = key
        self.variables = variables

    def __str__(self):
        return "Requested {key} and variables {variables} with but an error occured".format(
            key=self.key, variables=self.variables
        )


translations_yaml_max_cache = 0 if ENV == "dev" else None


@lru_cache(maxsize=translations_yaml_max_cache)
def _translations_file():
    file_name = "translations.yaml"

    if app:
        file_name = app.config.get("DEFAULT_TRANSLATIONS_FILE", file_name)

    f = open(file_name)

    return yaml.safe_load(f)


def translate(key, variables=None):
    translations = _translations_file()
    value = getattr_path(translations, key)

    if variables is None:
        variables = {}

    if value is None:
        raise LocalizationInvalidKeyError(key, variables)

    return value.format(**variables).replace("\n", "")
