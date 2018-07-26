import tornado

from atst.handler import BaseHandler
from atst.domain.workspaces import Members


class WorkspaceMembers(BaseHandler):
    def initialize(self):
        self.members_repo = Members()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, workspace_id):
        members = self.members_repo.get_many(workspace_id)
        self.render("workspace_members.html.to", members=members)
