# Add root application dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import sqlalchemy

from atst.database import db
from atst.app import make_config, make_app


def remove_sample_data():
    conn = db.engine.connect()

    meta = sqlalchemy.MetaData(bind=conn, reflect=True)
    trans = conn.begin()

    retained_tables = ["permission_sets"]

    for t in meta.sorted_tables:
        if str(t) not in retained_tables:
            conn.execute("ALTER TABLE {} DISABLE trigger ALL;".format(t))
            conn.execute(t.delete())
            conn.execute("ALTER TABLE {} ENABLE trigger ALL;".format(t))

    trans.commit()


if __name__ == "__main__":
    config = make_config({"DISABLE_CRL_CHECK": True, "DEBUG": False})
    app = make_app(config)
    with app.app_context():
        remove_sample_data()
