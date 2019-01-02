import yaml
import os
from flask import current_app as app
from functools import lru_cache
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


localizations_cache_size = 1 if ENV == "dev" else None


@lru_cache(maxsize=localizations_cache_size)
def load_cached_translations_file(file_name):
    return open(file_name).read()


def _translations_file():
    file_name = "translations.yaml"

    if app:
        file_name = app.config.get("TRANSLATIONS_FILE") or file_name

    return file_name


def translate(key, variables=None):
    translations_file = _translations_file()
    translations = yaml.safe_load(load_cached_translations_file(translations_file))
    value = getattr_path(translations, key)

    if variables is None:
        variables = {}

    if value is None:
        raise LocalizationInvalidKeyError(key, variables)

    return value.format(**variables).replace("\n", "")
