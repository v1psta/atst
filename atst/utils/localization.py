import yaml
import os
from functools import lru_cache
import math
from gettext import ngettext
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


@lru_cache(maxsize=None)
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


def translate_duration(duration_in_months):
    duration = []
    years = math.floor(duration_in_months / 12)
    months = duration_in_months % 12
    if years > 0:
        duration.append("{} {}".format(years, ngettext("year", "years", years)))
    if months > 0:
        duration.append("{} {}".format(months, ngettext("month", "months", months)))
    return (", ").join(duration)
