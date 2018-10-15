class FormValidationError(Exception):

    message = "Form validation failed."

    def __init__(self, form):
        self.form = form
