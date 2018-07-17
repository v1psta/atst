from wtforms_tornado import Form


class ValidatedForm(Form):

    def validate_warnings(self, *args, **kwargs):
        return True
