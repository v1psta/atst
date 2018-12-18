import pytest
from werkzeug.datastructures import FileStorage

from atst.models.attachment import Attachment, AttachmentError

from tests.mocks import PDF_FILENAME


def test_attach(pdf_upload):
    attachment = Attachment.attach(pdf_upload)
    assert attachment.filename == PDF_FILENAME
    assert attachment.object_name is not None


def test_attach_raises():
    with open(PDF_FILENAME, "rb") as fp:
        fs = FileStorage(fp, content_type="something/else")
        with pytest.raises(AttachmentError):
            Attachment.attach(fs)


def test_repr(pdf_upload):
    attachment = Attachment.attach(pdf_upload)
    assert attachment.filename in str(attachment)
    assert str(attachment.id) in str(attachment)
