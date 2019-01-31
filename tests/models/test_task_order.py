from werkzeug.datastructures import FileStorage
import pytest, datetime

from atst.models.attachment import Attachment
from atst.models.task_order import TaskOrder, Status

from tests.factories import random_future_date, random_past_date
from tests.mocks import PDF_FILENAME


class TestTaskOrderStatus:
    def test_pending_status(self):
        to = TaskOrder()
        assert to.status == Status.PENDING

        to = TaskOrder(number="42", start_date=random_future_date())
        assert to.status == Status.PENDING

    def test_active_status(self):
        to = TaskOrder(
            number="42", start_date=random_past_date(), end_date=random_future_date()
        )
        assert to.status == Status.ACTIVE

    def test_expired_status(self):
        to = TaskOrder(
            number="42", start_date=random_past_date(), end_date=random_past_date()
        )
        assert to.status == Status.EXPIRED


def test_is_submitted():
    to = TaskOrder()
    assert not to.is_submitted

    to = TaskOrder(
        number="42",
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=1),
    )
    assert to.is_submitted


class TestCSPEstimate:
    def test_setting_estimate_with_attachment(self):
        to = TaskOrder()
        attachment = Attachment(filename="sample.pdf", object_name="sample")
        to.csp_estimate = attachment

        assert to.attachment_id == attachment.id

    def test_setting_estimate_with_file_storage(self):
        to = TaskOrder()
        with open(PDF_FILENAME, "rb") as fp:
            fs = FileStorage(fp, content_type="application/pdf")
            to.csp_estimate = fs

        assert to.csp_estimate is not None
        assert to.csp_estimate.filename == PDF_FILENAME

    def test_setting_estimate_with_invalid_object(self):
        to = TaskOrder()
        with pytest.raises(TypeError):
            to.csp_estimate = "invalid"

    def test_setting_estimate_with_empty_value(self):
        to = TaskOrder()
        assert to.csp_estimate is None

        to.csp_estimate = ""
        assert to.csp_estimate is None

    def test_removing_estimate(self):
        attachment = Attachment(filename="sample.pdf", object_name="sample")
        to = TaskOrder(csp_estimate=attachment)
        assert to.csp_estimate is not None

        to.csp_estimate = ""
        assert to.csp_estimate is None
