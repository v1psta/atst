import os
import tarfile
from tempfile import NamedTemporaryFile, TemporaryDirectory
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


def get_rackspace_container(provider, container=None, **kwargs):
    if provider == "LOCAL":  # pragma: no branch
        kwargs["key"] = container
        container = ""

    driver = get_driver(getattr(Provider, provider))(**kwargs)
    return driver.get_container(container)


class RackspaceFileProvider(FileProviderInterface):
    def __init__(self, app):
        self.container = get_rackspace_container(
            provider=app.config.get("STORAGE_PROVIDER"),
            container=app.config.get("STORAGE_CONTAINER"),
            key=app.config.get("STORAGE_KEY"),
            secret=app.config.get("STORAGE_SECRET"),
        )

    def upload(self, fyle):
        self._enforce_mimetype(fyle)

        object_name = uuid4().hex
        with NamedTemporaryFile() as tempfile:
            tempfile.write(fyle.stream.read())
            tempfile.seek(0)
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


class CRLProviderInterface:
    def sync_crls(self):  # pragma: no cover
        """
        Retrieve copies of the CRLs and unpack them to disk.
        """
        raise NotImplementedError()


class RackspaceCRLProvider(CRLProviderInterface):
    def __init__(self, app):
        self.container = get_rackspace_container(
            provider=app.config.get("STORAGE_PROVIDER"),
            container=app.config.get("CRL_CONTAINER"),
            key=app.config.get("STORAGE_KEY"),
            secret=app.config.get("STORAGE_SECRET"),
            region=app.config.get("CRL_REGION"),
        )
        self._crl_dir = app.config.get("CRL_CONTAINER")
        self._object_name = app.config.get("STORAGE_CRL_ARCHIVE_NAME")

    def sync_crls(self):
        if not os.path.exists(self._crl_dir):
            os.mkdir(self._crl_dir)

        obj = self.container.get_object(object_name=self._object_name)
        with TemporaryDirectory() as tempdir:
            dl_path = os.path.join(tempdir, self._object_name)
            obj.download(dl_path, overwrite_existing=True)
            archive = tarfile.open(dl_path, "r:bz2")
            archive.extractall(self._crl_dir)
