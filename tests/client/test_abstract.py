from healthchecks_io.client._abstract import AbstractClient


def test_abstract_add_url_params():
    AbstractClient.__abstractmethods__ = set()
    abstract_client = AbstractClient("test")
    url = abstract_client._add_url_params(
        "http://test.com/?test=test", {"test": "test2"}
    )
    assert url == "http://test.com/?test=test2"
