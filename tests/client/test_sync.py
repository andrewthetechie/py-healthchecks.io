from urllib.parse import urljoin

import pytest
import respx
from httpx import Client as HTTPXClient
from httpx import Response

from healthchecks_io import CheckCreate
from healthchecks_io import CheckUpdate
from healthchecks_io import Client
from healthchecks_io.client.exceptions import BadAPIRequestError
from healthchecks_io.client.exceptions import CheckNotFoundError
from healthchecks_io.client.exceptions import HCAPIAuthError
from healthchecks_io.client.exceptions import HCAPIError


@pytest.mark.respx
def test_create_check_200(fake_check_api_result, respx_mock, test_client):
    checks_url = urljoin(test_client._api_url, "checks/")
    respx_mock.post(checks_url).mock(
        return_value=Response(
            status_code=200,
            json={
                "channels": "",
                "desc": "",
                "grace": 60,
                "last_ping": None,
                "n_pings": 0,
                "name": "Backups",
                "slug": "backups",
                "next_ping": None,
                "manual_resume": False,
                "methods": "",
                "pause_url": "https://healthchecks.io/api/v1/checks/f618072a-7bde-4eee-af63-71a77c5723bc/pause",
                "ping_url": "https://hc-ping.com/f618072a-7bde-4eee-af63-71a77c5723bc",
                "status": "new",
                "tags": "prod www",
                "timeout": 3600,
                "update_url": "https://healthchecks.io/api/v1/checks/f618072a-7bde-4eee-af63-71a77c5723bc",
            },
        )
    )
    check = test_client.create_check(CheckCreate(name="test", tags="test", desc="test"))
    assert check.name == "Backups"


@pytest.mark.respx
def test_update_check_200(fake_check_api_result, respx_mock, test_client):
    checks_url = urljoin(test_client._api_url, "checks/test")
    respx_mock.post(checks_url).mock(
        return_value=Response(
            status_code=200,
            json={
                "channels": "",
                "desc": "",
                "grace": 60,
                "last_ping": None,
                "n_pings": 0,
                "name": "Backups",
                "slug": "backups",
                "next_ping": None,
                "manual_resume": False,
                "methods": "",
                "pause_url": "https://healthchecks.io/api/v1/checks/f618072a-7bde-4eee-af63-71a77c5723bc/pause",
                "ping_url": "https://hc-ping.com/f618072a-7bde-4eee-af63-71a77c5723bc",
                "status": "new",
                "tags": "prod www",
                "timeout": 3600,
                "update_url": "https://healthchecks.io/api/v1/checks/f618072a-7bde-4eee-af63-71a77c5723bc",
            },
        )
    )
    check = test_client.update_check("test", CheckUpdate(name="test", desc="test"))
    assert check.name == "Backups"


@pytest.mark.respx
def test_get_checks_200(fake_check_api_result, respx_mock, test_client):
    assert test_client._client is not None
    checks_url = urljoin(test_client._api_url, "checks/")
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json={"checks": [fake_check_api_result]})
    )
    checks = test_client.get_checks()
    assert len(checks) == 1
    assert checks[0].name == fake_check_api_result["name"]


@pytest.mark.respx
def test_get_checks_pass_in_client(fake_check_api_result, respx_mock):
    httpx_client = HTTPXClient()
    test_client = Client(
        api_key="test", api_url="http://localhost/api/", client=httpx_client
    )
    checks_url = urljoin(test_client._api_url, "checks/")
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json={"checks": [fake_check_api_result]})
    )
    checks = test_client.get_checks()
    assert len(checks) == 1
    assert checks[0].name == fake_check_api_result["name"]


@pytest.mark.respx
def test_get_checks_exceptions(fake_check_api_result, respx_mock, test_client):
    checks_url = urljoin(test_client._api_url, "checks/")
    # test exceptions
    respx_mock.get(checks_url).mock(return_value=Response(status_code=401))
    with pytest.raises(HCAPIAuthError):
        test_client.get_checks()

    respx_mock.get(checks_url).mock(return_value=Response(status_code=500))
    with pytest.raises(HCAPIError):
        test_client.get_checks()


@pytest.mark.respx
def test_get_checks_tags(fake_check_api_result, respx_mock, test_client):
    """Test get_checks with tags"""
    checks_url = urljoin(test_client._api_url, "checks/")
    respx_mock.get(f"{checks_url}?tag=test&tag=test2").mock(
        return_value=Response(status_code=200, json={"checks": [fake_check_api_result]})
    )
    checks = test_client.get_checks(tags=["test", "test2"])
    assert len(checks) == 1
    assert checks[0].name == fake_check_api_result["name"]


def test_finalizer_closes(test_client):
    """Tests our finalizer works to close the method"""
    assert not test_client.is_closed
    test_client._finalizer_method()
    assert test_client.is_closed


@pytest.mark.respx
def test_get_check_200(fake_check_api_result, respx_mock, test_client):
    assert test_client._client is not None
    checks_url = urljoin(test_client._api_url, "checks/test")
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json=fake_check_api_result)
    )
    check = test_client.get_check(check_id="test")
    assert check.name == fake_check_api_result["name"]


@pytest.mark.respx
def test_check_get_404(respx_mock, test_client):
    assert test_client._client is not None
    checks_url = urljoin(test_client._api_url, "checks/test")
    respx_mock.get(checks_url).mock(return_value=Response(status_code=404))
    with pytest.raises(CheckNotFoundError):
        test_client.get_check("test")


@pytest.mark.respx
def test_pause_check_200(fake_check_api_result, respx_mock, test_client):
    checks_url = urljoin(test_client._api_url, "checks/test/pause")
    respx_mock.post(checks_url).mock(
        return_value=Response(status_code=200, json=fake_check_api_result)
    )
    check = test_client.pause_check(check_id="test")
    assert check.name == fake_check_api_result["name"]


@pytest.mark.respx
def test_check_pause_404(respx_mock, test_client):
    assert test_client._client is not None
    checks_url = urljoin(test_client._api_url, "checks/test/pause")
    respx_mock.post(checks_url).mock(return_value=Response(status_code=404))
    with pytest.raises(CheckNotFoundError):
        test_client.pause_check("test")


@pytest.mark.respx
def test_delete_check_200(fake_check_api_result, respx_mock, test_client):
    assert test_client._client is not None
    checks_url = urljoin(test_client._api_url, "checks/test")
    respx_mock.delete(checks_url).mock(
        return_value=Response(status_code=200, json=fake_check_api_result)
    )
    check = test_client.delete_check(check_id="test")
    assert check.name == fake_check_api_result["name"]


@pytest.mark.respx
def test_delete_pause404(respx_mock, test_client):
    checks_url = urljoin(test_client._api_url, "checks/test")
    respx_mock.delete(checks_url).mock(return_value=Response(status_code=404))
    with pytest.raises(CheckNotFoundError):
        test_client.delete_check("test")


@pytest.mark.respx
def test_get_check_pings_200(fake_check_pings_api_result, respx_mock, test_client):
    checks_url = urljoin(test_client._api_url, "checks/test/pings/")
    respx_mock.get(checks_url).mock(
        return_value=Response(
            status_code=200, json={"pings": fake_check_pings_api_result}
        )
    )
    pings = test_client.get_check_pings("test")
    assert len(pings) == len(fake_check_pings_api_result)
    assert pings[0].type == fake_check_pings_api_result[0]["type"]


@pytest.mark.respx
def test_get_check_flips_200(fake_check_flips_api_result, respx_mock, test_client):
    checks_url = urljoin(test_client._api_url, "checks/test/flips/")
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json=fake_check_flips_api_result)
    )
    flips = test_client.get_check_flips("test")
    assert len(flips) == len(fake_check_flips_api_result)
    assert flips[0].up == fake_check_flips_api_result[0]["up"]


@pytest.mark.respx
def test_get_check_flips_params_200(
    fake_check_flips_api_result, respx_mock, test_client
):
    checks_url = urljoin(
        test_client._api_url, "checks/test/flips/?seconds=1&start=1&end=1"
    )
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json=fake_check_flips_api_result)
    )
    flips = test_client.get_check_flips("test", seconds=1, start=1, end=1)
    assert len(flips) == len(fake_check_flips_api_result)
    assert flips[0].up == fake_check_flips_api_result[0]["up"]


@pytest.mark.respx
def test_get_check_flips_400(fake_check_flips_api_result, respx_mock, test_client):
    flips_url = urljoin(test_client._api_url, "checks/test/flips/")
    respx_mock.get(flips_url).mock(return_value=Response(status_code=400))
    with pytest.raises(BadAPIRequestError):
        test_client.get_check_flips("test")


@pytest.mark.respx
def test_get_integrations(fake_integrations_api_result, respx_mock, test_client):
    channels_url = urljoin(test_client._api_url, "channels/")
    respx_mock.get(channels_url).mock(
        return_value=Response(status_code=200, json=fake_integrations_api_result)
    )
    integrations = test_client.get_integrations()
    assert len(integrations) == len(fake_integrations_api_result["channels"])
    assert integrations[0].id == fake_integrations_api_result["channels"][0]["id"]


@pytest.mark.respx
def test_get_badges(fake_badges_api_result, respx_mock, test_client):
    channels_url = urljoin(test_client._api_url, "badges/")
    respx_mock.get(channels_url).mock(
        return_value=Response(status_code=200, json=fake_badges_api_result)
    )
    integrations = test_client.get_badges()
    assert integrations.keys() == fake_badges_api_result["badges"].keys()


ping_test_parameters = [
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "test",
        "success_ping",
        {"uuid": "test"},
    ),
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "1234/test",
        "success_ping",
        {"slug": "test"},
    ),
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "test/start",
        "start_ping",
        {"uuid": "test"},
    ),
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "1234/test/start",
        "start_ping",
        {"slug": "test"},
    ),
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "test/fail",
        "fail_ping",
        {"uuid": "test"},
    ),
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "1234/test/fail",
        "fail_ping",
        {"slug": "test"},
    ),
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "test/0",
        "exit_code_ping",
        {"exit_code": 0, "uuid": "test"},
    ),
    (
        pytest.lazy_fixture("respx_mock"),
        pytest.lazy_fixture("test_client"),
        "1234/test/0",
        "exit_code_ping",
        {"exit_code": 0, "slug": "test"},
    ),
]


@pytest.mark.respx
@pytest.mark.parametrize(
    "respx_mocker, tc, url, ping_method, method_kwargs", ping_test_parameters
)
def test_success_ping(respx_mocker, tc, url, ping_method, method_kwargs):
    channels_url = urljoin(tc._ping_url, url)
    respx_mocker.get(channels_url).mock(
        return_value=Response(status_code=200, text="OK")
    )
    ping_method = getattr(tc, ping_method)
    result, text = ping_method(**method_kwargs)
    assert result is True
    assert text == "OK"
