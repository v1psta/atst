from flask_wtf import FlaskForm
from flask import current_app, request as http_request

from atst.utils.flash import formatted_flash as flash


class BaseForm(FlaskForm):
    def __init__(self, formdata=None, **kwargs):
        formdata = formdata or {}
        cached_data = current_app.form_cache.from_request(http_request)
        cached_data.update(formdata)
        super().__init__(cached_data, **kwargs)

    @property
    def data(self):
        _data = super().data
        _data.pop("csrf_token", None)
        return _data

    def validate(self, *args, **kwargs):
        valid = super().validate(*args, **kwargs)
        if not valid:
            flash("form_errors")
        return valid
