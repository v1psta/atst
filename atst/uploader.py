from uuid import uuid4
from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver


class UploadError(Exception):
    pass


class Uploader:
    _PERMITTED_MIMETYPES = ["application/pdf"]

    def __init__(self, provider, container=None, key=None, secret=None):
        self.container = self._get_container(provider, container, key, secret)

    def upload(self, fyle):
        # TODO: for hardening, we should probably use a better library for
        # determining mimetype and not rely on FileUpload's determination
        # TODO: we should set MAX_CONTENT_LENGTH in the config to prevent large
        # uploads
        if not fyle.mimetype in self._PERMITTED_MIMETYPES:
            raise UploadError(
                "could not upload {} with mimetype {}".format(
                    fyle.filename, fyle.mimetype
                )
            )

        object_name = uuid4().hex
        self.container.upload_object_via_stream(
            iterator=fyle.stream.__iter__(),
            object_name=object_name,
            extra={"acl": "private"},
        )
        return (fyle.filename, object_name)

    def download(self, path):
        pass

    def _get_container(self, provider, container, key, secret):
        if provider == "LOCAL":
            key = container
            container = ""

        driver = get_driver(getattr(Provider, provider))(key=key, secret=secret)
        return driver.get_container(container)
