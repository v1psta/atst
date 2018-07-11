from wtforms_tornado import Form


class ValidatedForm(Form):

    def validate(self, requests_client=None):
        return super(ValidatedForm, self).validate()
