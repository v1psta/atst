import yaml
from flask import current_app as app
from atst.utils import getattr_path


class LocalizationInvalidKeyError(Exception):
    def __init__(self, key, variables):
        self.key = key
        self.variables = variables

    def __str__(self):
        return "Requested {key} and variables {variables} with but an error occured".format(
            key=self.key, variables=self.variables
        )


def _translations_file():
    file_name = "translations.yaml"

    if app:
        file_name = app.config.get("DEFAULT_TRANSLATIONS_FILE", file_name)

    return open(file_name)


def translate(key, variables=None):
    translations_file = _translations_file()
    translations = yaml.safe_load(translations_file)
    value = getattr_path(translations, key)

    if variables is None:
        variables = {}

    if value is None:
        raise LocalizationInvalidKeyError(key, variables)

    return value.format(**variables).replace("\n", "")
