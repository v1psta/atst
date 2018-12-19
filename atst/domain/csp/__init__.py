from .files import RackspaceFileProvider


class MockCSP:

    def __init__(self, file_provider):
        self.files = file_provider


def make_csp_provider(app):
    app.csp = MockCSP(RackspaceFileProvider(app))
