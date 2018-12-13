from flask import url_for

from atst.database import db
from atst.models.workspace import Workspace


def get_workspace_by_name(name):
    return db.session.query(Workspace).filter_by(name=name).one()


def test_get_new_workspace(client, user_session):
    user_session()
    response = client.get(url_for("workspaces.new"))
    assert response.status_code == 200


def test_create_new_workspace(client, user_session):
    user_session()
    ws_name = "mos-eisley"
    response = client.post(
        url_for("workspaces.create"), data={"name": ws_name}, follow_redirects=False
    )
    assert response.status_code == 302
    workspace = get_workspace_by_name(ws_name)
    assert workspace.name == ws_name
    task_order = workspace.task_orders[0]
    assert str(task_order.id) in response.headers.get("Location")
