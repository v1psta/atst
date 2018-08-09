class NotFoundError(Exception):
    def __init__(self, resource_name):
        self.resource_name = resource_name

    @property
    def message(self):
        return "No {} could be found.".format(self.resource_name)


class AlreadyExistsError(Exception):
    def __init__(self, resource_name):
        self.resource_name = resource_name

    @property
    def message(self):
        return "{} already exists".format(self.resource_name)


class UnauthorizedError(Exception):
    def __init__(self, user, action):
        self.user = user
        self.action = action

    @property
    def message(self):
        return "User {} not authorized to {}".format(self.user.id, self.action)


class UnauthenticatedError(Exception):
    @property
    def message(self):
        return str(self)


class CRLValidationError(Exception):
    pass
