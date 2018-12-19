from atst.uploader import Uploader


class FileProviderInterface:
    def upload(self, fyle): # pragma: no cover
        """Store the file object `fyle` in the CSP. This method returns the
        object name that can be used to later look up the file."""
        raise NotImplementedError()

    def download(self, object_name): # pragma: no cover
        """Retrieve the stored file represented by `object_name`. Returns a
        file object.
        """
        raise NotImplementedError()


class RackspaceFileProvider(FileProviderInterface):
    def __init__(self, app):
        self.uploader = Uploader(
            provider=app.config.get("STORAGE_PROVIDER"),
            container=app.config.get("STORAGE_CONTAINER"),
            key=app.config.get("STORAGE_KEY"),
            secret=app.config.get("STORAGE_SECRET"),
        )

    def upload(self, fyle):
        return self.uploader.upload(fyle)

    def download(self, object_name):
        return self.uploader.download_stream(object_name)
