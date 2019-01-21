from tempfile import NamedTemporaryFile
from uuid import uuid4

from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver

from atst.domain.exceptions import UploadError


class FileProviderInterface:
    _PERMITTED_MIMETYPES = ["application/pdf", "image/png"]

    def _enforce_mimetype(self, fyle):
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

    def upload(self, fyle):  # pragma: no cover
        """Store the file object `fyle` in the CSP. This method returns the
        object name that can be used to later look up the file."""
        raise NotImplementedError()

    def download(self, object_name):  # pragma: no cover
        """Retrieve the stored file represented by `object_name`. Returns a
        file object.
        """
        raise NotImplementedError()


class RackspaceFileProvider(FileProviderInterface):
    def __init__(self, app):
        self.container = self._get_container(
            provider=app.config.get("STORAGE_PROVIDER"),
            container=app.config.get("STORAGE_CONTAINER"),
            key=app.config.get("STORAGE_KEY"),
            secret=app.config.get("STORAGE_SECRET"),
        )

    def _get_container(self, provider, container=None, key=None, secret=None):
        if provider == "LOCAL":  # pragma: no branch
            key = container
            container = ""

        driver = get_driver(getattr(Provider, provider))(key=key, secret=secret)
        return driver.get_container(container)

    def upload(self, fyle):
        self._enforce_mimetype(fyle)

        object_name = uuid4().hex
        with NamedTemporaryFile() as tempfile:
            tempfile.write(fyle.stream.read())
            self.container.upload_object(
                file_path=tempfile.name,
                object_name=object_name,
                extra={"acl": "private"},
            )
        return object_name

    def download(self, object_name):
        obj = self.container.get_object(object_name=object_name)
        with NamedTemporaryFile() as tempfile:
            obj.download(tempfile.name, overwrite_existing=True)
            return open(tempfile.name, "rb")
