from copy import deepcopy

import pytest
from httpx import Request
from httpx import Response

from healthchecks_io import BadAPIRequestError
from healthchecks_io import CheckNotFoundError
from healthchecks_io import HCAPIAuthError
from healthchecks_io import HCAPIError
from healthchecks_io import HCAPIRateLimitError
from healthchecks_io import NonUniqueSlugError


def test_abstract_add_url_params(test_abstract_client):

    url = test_abstract_client._add_url_params(
        "http://test.com/?test=test", {"test": "test2"}
    )
    assert url == "http://test.com/?test=test2"


def test_get_ping_url(test_abstract_client):
    url = test_abstract_client._get_ping_url("test", "", "/endpoint")
    assert url == f"{test_abstract_client._ping_url}test/endpoint"

    # test for raising when we send both a slug and a uuid
    with pytest.raises(BadAPIRequestError):
        test_abstract_client._get_ping_url("uuid", "slug", "endpoint")

    # test for raising when we try a slug w/o a ping_key
    test_abstract_client._ping_key = ""
    with pytest.raises(BadAPIRequestError):
        test_abstract_client._get_ping_url("", "slug", "endpoint")


check_response_parameters = [
    (
        pytest.lazy_fixture("test_abstract_client"),
        Response(status_code=401, request=Request("get", "http://test")),
        HCAPIAuthError,
    ),
    (
        pytest.lazy_fixture("test_abstract_client"),
        Response(status_code=500, request=Request("get", "http://test")),
        HCAPIError,
    ),
    (
        pytest.lazy_fixture("test_abstract_client"),
        Response(status_code=429, request=Request("get", "http://test")),
        HCAPIRateLimitError,
    ),
    (
        pytest.lazy_fixture("test_abstract_client"),
        Response(status_code=404, request=Request("get", "http://test")),
        CheckNotFoundError,
    ),
    (
        pytest.lazy_fixture("test_abstract_client"),
        Response(status_code=400, request=Request("get", "http://test")),
        BadAPIRequestError,
    ),
]


@pytest.mark.parametrize("test_client, response, exception", check_response_parameters)
def test_check_resposne(test_client, response, exception):
    with pytest.raises(exception):
        test_client.check_response(response)


ping_response_parameters = deepcopy(check_response_parameters)
ping_response_parameters.append(
    (
        pytest.lazy_fixture("test_abstract_client"),
        Response(status_code=409, request=Request("get", "http://test")),
        NonUniqueSlugError,
    )
)


@pytest.mark.parametrize("test_client, response, exception", ping_response_parameters)
def test_check_ping_resposne(test_client, response, exception):
    with pytest.raises(exception):
        test_client.check_ping_response(response)
