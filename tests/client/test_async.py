from urllib.parse import urljoin

import pytest
import respx
from httpx import AsyncClient as HTTPXAsyncClient
from httpx import Response

from healthchecks_io.client import AsyncClient
from healthchecks_io.client.exceptions import HCAPIAuthError
from healthchecks_io.client.exceptions import HCAPIError


@pytest.mark.asyncio
@pytest.mark.respx
async def test_get_checks_200(fake_check_api_result, respx_mock, test_async_client):
    assert test_async_client._client is not None
    checks_url = urljoin(test_async_client._api_url, "checks/")
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json={"checks": [fake_check_api_result]})
    )
    checks = await test_async_client.get_checks()
    assert len(checks) == 1
    assert checks[0].name == fake_check_api_result["name"]


@pytest.mark.asyncio
@pytest.mark.respx
async def test_get_checks_pass_in_client(fake_check_api_result, respx_mock):
    httpx_client = HTTPXAsyncClient()
    test_async_client = AsyncClient(
        api_key="test", api_url="http://localhost/api/", client=httpx_client
    )
    checks_url = urljoin(test_async_client._api_url, "checks/")
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json={"checks": [fake_check_api_result]})
    )
    checks = await test_async_client.get_checks()
    assert len(checks) == 1
    assert checks[0].name == fake_check_api_result["name"]


@pytest.mark.asyncio
@pytest.mark.respx
async def test_get_checks_exceptions(
    fake_check_api_result, respx_mock, test_async_client
):
    checks_url = urljoin(test_async_client._api_url, "checks/")
    # test exceptions
    respx_mock.get(checks_url).mock(return_value=Response(status_code=401))
    with pytest.raises(HCAPIAuthError):
        await test_async_client.get_checks()

    respx_mock.get(checks_url).mock(return_value=Response(status_code=500))
    with pytest.raises(HCAPIError):
        await test_async_client.get_checks()


@pytest.mark.asyncio
@pytest.mark.respx
async def test_get_checks_tags(fake_check_api_result, respx_mock, test_async_client):
    """Test get_checks with tags"""
    checks_url = urljoin(test_async_client._api_url, "checks/")
    respx_mock.get(f"{checks_url}?tag=test&tag=test2").mock(
        return_value=Response(status_code=200, json={"checks": [fake_check_api_result]})
    )
    checks = await test_async_client.get_checks(tags=["test", "test2"])
    assert len(checks) == 1
    assert checks[0].name == fake_check_api_result["name"]


@pytest.mark.asyncio
def test_finalizer_closes(test_async_client):
    """Tests our finalizer works to close the method"""
    assert not test_async_client.is_closed
    test_async_client._finalizer_method()
    assert test_async_client.is_closed


@pytest.mark.asyncio
@pytest.mark.respx
async def test_get_check_200(fake_check_api_result, respx_mock, test_async_client):
    assert test_async_client._client is not None
    checks_url = urljoin(test_async_client._api_url, "checks/test")
    respx_mock.get(checks_url).mock(
        return_value=Response(status_code=200, json=fake_check_api_result)
    )
    check = await test_async_client.get_check(check_id="test")
    assert check.name == fake_check_api_result["name"]
