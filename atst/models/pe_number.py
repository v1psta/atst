from sqlalchemy import String, Column

from atst.models import Base


class PENumber(Base):
    __tablename__ = "pe_numbers"

    number = Column(String, primary_key=True)
    description = Column(String)

    def __repr__(self):  # pragma: no cover
        return "<PENumber(number='{}', description='{}')>".format(
            self.number, self.description
        )
