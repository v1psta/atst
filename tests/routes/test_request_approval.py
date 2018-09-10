import os
from flask import url_for

from atst.models.attachment import Attachment
from atst.domain.roles import Roles

from tests.factories import (
    RequestFactory, TaskOrderFactory, UserFactory, RequestReviewFactory
)


def test_ccpo_can_view_approval(user_session, client):
    ccpo = Roles.get("ccpo")
    user = UserFactory.create(atat_role=ccpo)
    user_session(user)

    request = RequestFactory.create()
    response = client.get(url_for("requests.approval", request_id=request.id))
    assert response.status_code == 200


def test_non_ccpo_cannot_view_approval(user_session, client):
    user = UserFactory.create()
    user_session(user)

    request = RequestFactory.create(creator=user)
    response = client.get(url_for("requests.approval", request_id=request.id))
    assert response.status_code == 404


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
    full_path = os.path.join(
        app.config.get("STORAGE_CONTAINER"), attachment.object_name
    )
    with open(full_path, "wb") as output_file:
        output_file.write(pdf_content)
        output_file.flush()

    response = client.get(
        url_for("requests.task_order_pdf_download", request_id=request.id)
    )
    assert response.data == pdf_content


def test_task_order_download_does_not_exist(client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create(creator=user)
    response = client.get(
        url_for("requests.task_order_pdf_download", request_id=request.id)
    )
    assert response.status_code == 404


def test_can_submit_request_approval(client, user_session):
    user = UserFactory.from_atat_role("ccpo")
    user_session(user)
    request = RequestFactory.create()
    review_data = RequestReviewFactory.dictionary()
    response = client.post(
        url_for("requests.submit_approval", request_id=request.id), data=review_data
    )
    assert response.status_code == 301
