import os
import pytest
from werkzeug.datastructures import FileStorage

from atst.uploader import Uploader, UploadError

from tests.mocks import PDF_FILENAME


@pytest.fixture(scope="function")
def upload_dir(tmpdir):
    return tmpdir.mkdir("uploads")


@pytest.fixture
def uploader(upload_dir):
    return Uploader("LOCAL", container=upload_dir)


NONPDF_FILENAME = "tests/fixtures/disa-pki.html"


def test_upload(uploader, upload_dir, pdf_upload):
    filename, object_name = uploader.upload(pdf_upload)
    assert filename == PDF_FILENAME
    assert os.path.isfile(os.path.join(upload_dir, object_name))


def test_upload_fails_for_non_pdfs(uploader):
    with open(NONPDF_FILENAME, "rb") as fp:
        fs = FileStorage(fp, content_type="text/plain")
        with pytest.raises(UploadError):
            uploader.upload(fs)
