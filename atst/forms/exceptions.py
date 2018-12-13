from atst.utils.localization import translate


class FormValidationError(Exception):

    message = translate("forms.exceptions.message")

    def __init__(self, form):
        self.form = form
