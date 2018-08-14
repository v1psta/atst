from flask_wtf import FlaskForm


class ValidatedForm(FlaskForm):
    def perform_extra_validation(self, *args, **kwargs):
        """Performs any applicable extra validation. Must
        return True if the form is valid or False otherwise."""
        return True

    @property
    def data(self):
        _data = super().data
        _data.pop("csrf_token", None)
        return _data
