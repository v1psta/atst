from flask import url_for
from io import BytesIO
import re
from zipfile import ZipFile

from atst.utils.docx import Docx

from tests.factories import TaskOrderFactory, PortfolioFactory, UserFactory


def xml_translated(val):
    val = re.sub("'", "&#39;", str(val))
    val = re.sub(" & ", " &amp; ", str(val))
    return val


def test_download_summary(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    task_order = TaskOrderFactory.create(creator=user, portfolio=portfolio)
    user_session(user)
    response = client.get(
        url_for("task_orders.download_summary", task_order_id=task_order.id)
    )
    bytes_str = BytesIO(response.data)
    zip_ = ZipFile(bytes_str, mode="r")
    doc = zip_.read(Docx.DOCUMENT_FILE).decode()
    for attr, val in task_order.to_dictionary().items():
        assert attr in doc
        assert xml_translated(val) in doc


class TestDownloadCSPEstimate:
    def setup(self):
        self.user = UserFactory.create()
        self.portfolio = PortfolioFactory.create(owner=self.user)
        self.task_order = TaskOrderFactory.create(
            creator=self.user, portfolio=self.portfolio
        )

    def test_successful_download(self, client, user_session, pdf_upload):
        self.task_order.csp_estimate = pdf_upload
        user_session(self.user)
        response = client.get(
            url_for(
                "task_orders.download_csp_estimate", task_order_id=self.task_order.id
            )
        )
        assert response.status_code == 200

        pdf_upload.seek(0)
        expected_contents = pdf_upload.read()
        assert expected_contents == response.data

    def test_download_without_attachment(self, client, user_session):
        self.task_order.csp_attachment_id = None
        user_session(self.user)
        response = client.get(
            url_for(
                "task_orders.download_csp_estimate", task_order_id=self.task_order.id
            )
        )
        assert response.status_code == 404

    def test_download_with_wrong_user(self, client, user_session):
        other_user = UserFactory.create()
        user_session(other_user)
        response = client.get(
            url_for(
                "task_orders.download_csp_estimate", task_order_id=self.task_order.id
            )
        )
        assert response.status_code == 404
