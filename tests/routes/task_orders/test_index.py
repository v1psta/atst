from flask import url_for
from io import BytesIO
import re
from zipfile import ZipFile

from atst.utils.docx import Docx

from tests.factories import TaskOrderFactory


def xml_translated(val):
    return re.sub("'", "&#39;", str(val))


def test_download_summary(client, user_session):
    user_session()
    task_order = TaskOrderFactory.create()
    response = client.get(
        url_for("task_orders.download_summary", task_order_id=task_order.id)
    )
    bytes_str = BytesIO(response.data)
    zip_ = ZipFile(bytes_str, mode="r")
    doc = zip_.read(Docx.DOCUMENT_FILE).decode()
    for attr, val in task_order.to_dictionary().items():
        assert attr in doc
        if not xml_translated(val) in doc:
            __import__("ipdb").set_trace()
        assert xml_translated(val) in doc
