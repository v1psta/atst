from .cloud import MockCloudProvider
from .files import RackspaceFileProvider, RackspaceCRLProvider
from .reports import MockReportingProvider


class MockCSP:
    def __init__(self, app):
        self.cloud = MockCloudProvider()
        self.files = RackspaceFileProvider(app)
        self.reports = MockReportingProvider()
        self.crls = RackspaceCRLProvider(app)


def make_csp_provider(app):
    app.csp = MockCSP(app)
