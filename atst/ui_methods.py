import os

def dev(self):
    return os.getenv("TORNADO_ENV", "dev") == "dev"

def matchesPath(self, href):
    return self.request.uri.startswith(href)

def modal(self, body):
    return self.render_string(
      "components/modal.html.to",
      body=body)

def modalOpen(self):
    # For now, just check a dummy URL param
    return self.get_argument("modal", False)
