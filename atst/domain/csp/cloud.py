from uuid import uuid4


class CloudProviderInterface:
    def create_application(self, name):  # pragma: no cover
        """Create an application in the cloud with the provided name. Returns
        the ID of the created object.
        """
        raise NotImplementedError()

    def create_role(self, environment_role):  # pragma: no cover
        """Takes an `atst.model.EnvironmentRole` object and allows the
        specified user access to the specified cloud entity.

        This _does not_ return a token, but is intended to perform any necessary
        setup to allow a token to be generated in the future (for example,
        add the user to the cloud entity in some fashion).
        """
        raise NotImplementedError()

    def delete_role(self, environment_role):  # pragma: no cover
        """Takes an `atst.model.EnvironmentRole` object and performs any action
        necessary in the CSP to remove the specified user from the specified
        environment. This method does not return anything.
        """
        raise NotImplementedError()


class MockCloudProvider(CloudProviderInterface):
    def create_application(self, name):
        """Returns an id that represents what would be an application in the
        cloud."""
        return uuid4().hex

    def create_role(self, environment_role):
        # Currently, there is nothing to mock out, so just do nothing.
        pass

    def delete_role(self, environment_role):
        # Currently nothing to do.
        pass
