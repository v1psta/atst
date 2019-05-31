from werkzeug.datastructures import FileStorage
import pytest, datetime

from atst.models.attachment import Attachment
from atst.models.task_order import TaskOrder, Status

from tests.factories import random_future_date, random_past_date
from tests.mocks import PDF_FILENAME


class TestTaskOrderStatus:
    @pytest.mark.skip(reason="Reimplement after adding CLINs")
    def test_started_status(self):
        to = TaskOrder()
        assert to.status == Status.STARTED

    @pytest.mark.skip(reason="See if still needed after implementing CLINs")
    def test_pending_status(self):
        to = TaskOrder(number="42")
        assert to.status == Status.PENDING

    @pytest.mark.skip(reason="See if still needed after implementing CLINs")
    def test_active_status(self):
        to = TaskOrder(number="42")
        assert to.status == Status.ACTIVE

    @pytest.mark.skip(reason="See if still needed after implementing CLINs")
    def test_expired_status(self):
        to = TaskOrder(number="42")
        assert to.status == Status.EXPIRED


class TestPDF:
    def test_setting_pdf_with_attachment(self):
        to = TaskOrder()
        attachment = Attachment(filename="sample.pdf", object_name="sample")
        to.pdf = attachment

        assert to.pdf_attachment_id == attachment.id

    def test_setting_pdf_with_file_storage(self):
        to = TaskOrder()
        with open(PDF_FILENAME, "rb") as fp:
            fs = FileStorage(fp, content_type="application/pdf")
            to.pdf = fs

        assert to.pdf is not None
        assert to.pdf.filename == PDF_FILENAME

    def test_setting_pdf_with_invalid_object(self):
        to = TaskOrder()
        with pytest.raises(TypeError):
            to.pdf = "invalid"

    def test_setting_pdf_with_empty_value(self):
        to = TaskOrder()
        assert to.pdf is None

        to.pdf = ""
        assert to.pdf is None

    def test_removing_pdf(self):
        attachment = Attachment(filename="sample.pdf", object_name="sample")
        to = TaskOrder(pdf=attachment)
        assert to.pdf is not None

        to.pdf = ""
        assert to.pdf is None
