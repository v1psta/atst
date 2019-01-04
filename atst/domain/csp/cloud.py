from uuid import uuid4


class CloudProviderInterface:
    def create_application(self, name):  # pragma: no cover
        """Create an application in the cloud with the provided name. Returns
        the ID of the created object.
        """
        raise NotImplementedError()


class MockCloudProvider(CloudProviderInterface):
    def create_application(self, name):
        """Returns an id that represents what would be an application in the
        cloud."""
        return uuid4().hex
