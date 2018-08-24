from sqlalchemy.dialects.postgresql import insert

from atst.database import db
from atst.models.pe_number import PENumber
from .exceptions import NotFoundError


class PENumbers(object):
    @classmethod
    def get(cls, number):
        pe_number = db.session.query(PENumber).get(number)
        if not pe_number:
            raise NotFoundError("pe_number")

        return pe_number

    @classmethod
    def create_many(cls, list_of_pe_numbers):
        stmt = insert(PENumber).values(list_of_pe_numbers)
        do_update = stmt.on_conflict_do_update(
            index_elements=["number"], set_=dict(description=stmt.excluded.description)
        )
        db.session.execute(do_update)
        db.session.commit()
