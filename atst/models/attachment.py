from sqlalchemy import Column, Integer, String
from flask import current_app as app

from atst.models import Base
from atst.database import db
from atst.uploader import UploadError


class AttachmentError(Exception):
    pass


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    object_name = Column(String, unique=True)

    @classmethod
    def attach(cls, fyle):
        try:
            filename, object_name = app.uploader.upload(fyle)
        except UploadError as e:
            raise AttachmentError("Could not add attachment. " + str(e))

        attachment = Attachment(filename=filename, object_name=object_name)

        db.session.add(attachment)
        db.session.commit()

        return attachment
