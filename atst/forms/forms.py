from flask_wtf import FlaskForm


class ValidatedForm(FlaskForm):
    def perform_extra_validation(self, *args, **kwargs):
        """Performs any applicable extra validation. Must
        return True if the form is valid or False otherwise."""
        return True
