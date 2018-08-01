import tornado
from tornado.gen import Return
from flask_wtf import FlaskForm


class ValidatedForm(FlaskForm):

    @tornado.gen.coroutine
    def perform_extra_validation(self, *args, **kwargs):
        """A coroutine that performs any applicable extra validation. Must
        return True if the form is valid or False otherwise."""
        raise Return(True)
