from .cloud import MockCloudProvider
from .file_uploads import AwsUploader, AzureUploader, MockUploader
from .reports import MockReportingProvider


class MockCSP:
    def __init__(self, app):
        self.cloud = MockCloudProvider()
        self.files = MockUploader(app)
        self.reports = MockReportingProvider()


class AzureCSP:
    def __init__(self, app):
        self.cloud = MockCloudProvider()
        self.files = AzureUploader(app.config)
        self.reports = MockReportingProvider()


class AwsCSP:
    def __init__(self, app):
        self.cloud = MockCloudProvider()
        self.files = AwsUploader(app.config)
        self.reports = MockReportingProvider()


def make_csp_provider(app, csp=None):
    if csp == "aws":
        app.csp = AwsCSP(app)
    elif csp == "azure":
        app.csp = AzureCSP(app)
    else:
        app.csp = MockCSP(app)
