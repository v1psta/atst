import os
import pytest
from werkzeug.datastructures import FileStorage

from atst.domain.csp.files import RackspaceFileProvider
from atst.domain.exceptions import UploadError

from tests.mocks import PDF_FILENAME


@pytest.fixture
def uploader(app):
    return RackspaceFileProvider(app)


NONPDF_FILENAME = "tests/fixtures/disa-pki.html"


def test_upload(app, uploader, pdf_upload):
    object_name = uploader.upload(pdf_upload)
    upload_dir = app.config["STORAGE_CONTAINER"]
    assert os.path.isfile(os.path.join(upload_dir, object_name))


def test_upload_fails_for_non_pdfs(uploader):
    with open(NONPDF_FILENAME, "rb") as fp:
        fs = FileStorage(fp, content_type="text/plain")
        with pytest.raises(UploadError):
            uploader.upload(fs)


def test_download(app, uploader, pdf_upload):
    # write pdf content to upload file storage and make sure it is flushed to
    # disk
    pdf_upload.seek(0)
    pdf_content = pdf_upload.read()
    pdf_upload.close()
    upload_dir = app.config["STORAGE_CONTAINER"]
    full_path = os.path.join(upload_dir, "abc")
    with open(full_path, "wb") as output_file:
        output_file.write(pdf_content)
        output_file.flush()

    stream = uploader.download("abc")
    stream_content = b"".join([b for b in stream])
    assert pdf_content == stream_content
