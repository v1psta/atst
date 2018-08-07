from tests.factories import RequestFactory


def test_started_request_requires_mo_action():
    request = RequestFactory.create()
