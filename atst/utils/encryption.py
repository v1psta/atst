from cryptography.fernet import Fernet
from flask import current_app as app


def create_fernet():
    form_key = app.config.get("FORM_SECRET")
    return Fernet(form_key)


def encrypt_value(value):
    fernet = create_fernet()
    return fernet.encrypt(str(value).encode()).decode()


def decrypt_value(value):
    fernet = create_fernet()
    return fernet.decrypt(value.encode()).decode()
