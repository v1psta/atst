from wtforms_tornado import Form


class ValidatedForm(Form):

    def validate_warnings(self, requests_client=None):
        return True
