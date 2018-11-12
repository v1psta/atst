from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app as app

from atst.models import Base, types, mixins
from atst.database import db
from atst.uploader import UploadError
from atst.domain.exceptions import NotFoundError


class AttachmentError(Exception):
    pass


class Attachment(Base, mixins.TimestampsMixin):
    __tablename__ = "attachments"

    id = types.Id()
    filename = Column(String, nullable=False)
    object_name = Column(String, unique=True, nullable=False)
    resource = Column(String)
    resource_id = Column(UUID(as_uuid=True), index=True)

    @classmethod
    def attach(cls, fyle, resource=None, resource_id=None):
        try:
            filename, object_name = app.uploader.upload(fyle)
        except UploadError as e:
            raise AttachmentError("Could not add attachment. " + str(e))

        attachment = Attachment(
            filename=filename,
            object_name=object_name,
            resource=resource,
            resource_id=resource_id,
        )

        db.session.add(attachment)
        db.session.commit()

        return attachment

    @classmethod
    def get(cls, id_):
        try:
            return db.session.query(Attachment).filter_by(id=id_).one()
        except NoResultFound:
            raise NotFoundError("attachment")

    @classmethod
    def get_for_resource(cls, resource, resource_id):
        try:
            return (
                db.session.query(Attachment)
                .filter_by(resource=resource, resource_id=resource_id)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("attachment")

    @classmethod
    def delete_for_resource(cls, resource, resource_id):
        try:
            return (
                db.session.query(Attachment)
                .filter_by(resource=resource, resource_id=resource_id)
                .update({"resource_id": None})
            )
        except NoResultFound:
            raise NotFoundError("attachment")

    def __repr__(self):
        return "<Attachment(name='{}', id='{}')>".format(self.filename, self.id)
