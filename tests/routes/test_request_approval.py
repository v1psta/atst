import os
from flask import url_for

from atst.models.attachment import Attachment
from tests.factories import RequestFactory, TaskOrderFactory, UserFactory


def test_approval():
    pass


def test_task_order_download(app, client, user_session, pdf_upload):
    user = UserFactory.create()
    user_session(user)

    attachment = Attachment.attach(pdf_upload)
    task_order = TaskOrderFactory.create(number="abc123", pdf=attachment)
    request = RequestFactory.create(task_order=task_order, creator=user)

    # ensure that real data for pdf upload has been flushed to disk
    pdf_upload.seek(0)
    pdf_content = pdf_upload.read()
    pdf_upload.close()
    full_path = os.path.join(app.config.get("STORAGE_CONTAINER"), attachment.object_name)
    with open(full_path, "wb") as output_file:
        output_file.write(pdf_content)
        output_file.flush()

    response = client.get(url_for("requests.task_order_pdf_download", request_id=request.id))
    assert response.data == pdf_content


def test_task_order_download_does_not_exist(client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create(creator=user)
    response = client.get(url_for("requests.task_order_pdf_download", request_id=request.id))
    assert response.status_code == 404
