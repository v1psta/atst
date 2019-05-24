from cryptography.fernet import Fernet
from flask import current_app as app


def create_fernet():
    form_key = app.config.get("FORM_SECRET")
    return Fernet(form_key)


def encrypt_value(value):
    if app.config.get("ENCRYPT_HIDDEN_FIELDS"):
        fernet = create_fernet()
        return fernet.encrypt(str(value).encode()).decode()
    else:
        return value


def decrypt_value(value):
    if app.config.get("ENCRYPT_HIDDEN_FIELDS"):
        fernet = create_fernet()
        return fernet.decrypt(value.encode()).decode()
    else:
        return value
