import os

def dev(self):
    return os.getenv("TORNADO_ENV", "dev") == "dev"

def matchesPath(self, href):
    return self.request.uri.startswith(href)
