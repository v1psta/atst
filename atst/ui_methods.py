def matchesPath(self, href):
    return self.request.uri.startswith(href)
