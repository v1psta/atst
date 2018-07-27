import tornado

from atst.handler import BaseHandler
from atst.domain.workspaces import Projects


class Workspace(BaseHandler):
    def initialize(self):
        self.projects_repo = Projects()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, workspace_id):
        projects = self.projects_repo.get_many(workspace_id)
        self.render("workspace_projects.html.to", workspace_id=workspace_id, projects=projects)
