from io import BytesIO
from zipfile import ZipFile

from atst.utils.docx import Docx


def test_render_docx():
    data = {"droid_class": "R2"}
    docx_file = Docx.render(data=data)
    zip_ = ZipFile(docx_file, mode="r")
    document = zip_.read(Docx.DOCUMENT_FILE)
    assert b"droid_class: R2" in document
