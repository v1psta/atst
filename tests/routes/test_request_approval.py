import os
from flask import url_for

from atst.models.attachment import Attachment
from atst.models.request_status_event import RequestStatus
from atst.domain.roles import Roles

from tests.factories import (
    RequestFactory,
    TaskOrderFactory,
    UserFactory,
    RequestReviewFactory,
    RequestStatusEventFactory,
)


def test_ccpo_can_view_approval(user_session, client):
    ccpo = Roles.get("ccpo")
    user = UserFactory.create(atat_role=ccpo)
    user_session(user)

    request = RequestFactory.create()
    response = client.get(url_for("requests.approval", request_id=request.id))
    assert response.status_code == 200


def test_ccpo_prepopulated_as_mission_owner(user_session, client):
    user = UserFactory.from_atat_role("ccpo")
    user_session(user)

    request = RequestFactory.create_with_status(RequestStatus.PENDING_CCPO_ACCEPTANCE)
    response = client.get(url_for("requests.approval", request_id=request.id))

    body = response.data.decode()
    assert user.first_name in body
    assert user.last_name in body


def test_non_ccpo_cannot_view_approval(user_session, client):
    user = UserFactory.create()
    user_session(user)

    request = RequestFactory.create(creator=user)
    response = client.get(url_for("requests.approval", request_id=request.id))
    assert response.status_code == 404


def prepare_request_pending_approval(creator, pdf_attachment=None):
    task_order = TaskOrderFactory.create(number="abc123", pdf=pdf_attachment)
    return RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_APPROVAL,
        task_order=task_order,
        creator=creator,
    )


def test_ccpo_sees_pdf_link(user_session, client, pdf_upload):
    ccpo = UserFactory.from_atat_role("ccpo")
    user_session(ccpo)

    attachment = Attachment.attach(pdf_upload)
    request = prepare_request_pending_approval(ccpo, pdf_attachment=attachment)

    response = client.get(url_for("requests.approval", request_id=request.id))
    download_url = url_for("requests.task_order_pdf_download", request_id=request.id)

    body = response.data.decode()
    assert download_url in body


def test_ccpo_does_not_see_pdf_link_if_no_pdf(user_session, client, pdf_upload):
    ccpo = UserFactory.from_atat_role("ccpo")
    user_session(ccpo)

    request = prepare_request_pending_approval(ccpo)

    response = client.get(url_for("requests.approval", request_id=request.id))
    download_url = url_for("requests.task_order_pdf_download", request_id=request.id)

    body = response.data.decode()
    assert download_url not in body


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
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_ACCEPTANCE
    )
    review_data = RequestReviewFactory.dictionary()
    review_data["review"] = "approving"
    response = client.post(
        url_for("requests.submit_approval", request_id=request.id), data=review_data
    )
    assert response.status_code == 302
    assert request.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION


def test_can_submit_request_denial(client, user_session):
    user = UserFactory.from_atat_role("ccpo")
    user_session(user)
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_ACCEPTANCE
    )
    review_data = RequestReviewFactory.dictionary()
    review_data["review"] = "denying"
    response = client.post(
        url_for("requests.submit_approval", request_id=request.id), data=review_data
    )
    assert response.status_code == 302
    assert request.status == RequestStatus.CHANGES_REQUESTED


def test_ccpo_user_can_comment_on_request(client, user_session):
    user = UserFactory.from_atat_role("ccpo")
    user_session(user)
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_ACCEPTANCE
    )
    assert len(request.internal_comments) == 0

    comment_text = "This is the greatest request in the history of requests"
    comment_form_data = {"text": comment_text}
    response = client.post(
        url_for("requests.create_internal_comment", request_id=request.id),
        data=comment_form_data,
    )
    assert response.status_code == 302
    assert len(request.internal_comments) == 1
    assert request.internal_comments[0].text == comment_text


def test_comment_text_is_required(client, user_session):
    user = UserFactory.from_atat_role("ccpo")
    user_session(user)
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_ACCEPTANCE
    )
    assert len(request.internal_comments) == 0

    comment_form_data = {"text": ""}
    response = client.post(
        url_for("requests.create_internal_comment", request_id=request.id),
        data=comment_form_data,
    )
    assert response.status_code == 200
    assert len(request.internal_comments) == 0


def test_other_user_cannot_comment_on_request(client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_ACCEPTANCE
    )

    comment_text = "What is this even"
    comment_form_data = {"text": comment_text}
    response = client.post(
        url_for("requests.create_internal_comment", request_id=request.id),
        data=comment_form_data,
    )

    assert response.status_code == 404
