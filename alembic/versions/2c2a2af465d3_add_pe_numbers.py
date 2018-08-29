"""add PE numbers

Revision ID: 2c2a2af465d3
Revises: 0845b2f0f401
Create Date: 2018-08-27 16:26:51.707146

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from urllib.request import urlopen
import csv

from atst.app import make_config
from atst.models.pe_number import PENumber


# revision identifiers, used by Alembic.
revision = '2c2a2af465d3'
down_revision = '0845b2f0f401'
branch_labels = None
depends_on = None


def get_pe_numbers(url):
    response = urlopen(url)
    t = response.read().decode("utf-8")
    return list(csv.reader(t.split("\r\n")))


def upgrade():
    config = make_config()
    pe_numbers = get_pe_numbers(config["PE_NUMBER_CSV_URL"])
    db = op.get_bind()
    stmt = insert(PENumber).values(pe_numbers)
    do_update = stmt.on_conflict_do_update(
        index_elements=["number"], set_=dict(description=stmt.excluded.description)
    )
    db.execute(do_update)


def downgrade():
    db = op.get_bind()
    db.execute("TRUNCATE TABLE pe_number")
