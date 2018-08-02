import os
import re


def navigationContext(self):
    return (
        "workspace"
        if re.match("\/workspaces\/[A-Za-z0-9]*", self.request.uri)
        else "global"
    )


def dev(self):
    return os.getenv("FLASK_ENV", "dev") == "dev"


def matchesPath(self, href):
    return re.match("^" + href, self.request.uri)


def modal(self, body):
    return self.render_string("components/modal.html.to", body=body)


def modalOpen(self):
    # For now, just check a dummy URL param
    return self.get_argument("modal", False)
