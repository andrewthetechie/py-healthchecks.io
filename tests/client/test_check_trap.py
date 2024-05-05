from urllib.parse import urljoin

import pytest
from httpx import Response

from healthchecks_io import CheckTrap
from healthchecks_io import PingFailedError
from healthchecks_io import WrongClientError


@pytest.mark.respx
def test_check_trap_sync(respx_mock, test_client):
    start_url = urljoin(test_client._ping_url, "test/start")
    respx_mock.post(start_url).mock(return_value=Response(status_code=200, text="OK"))
    success_url = urljoin(test_client._ping_url, "test")
    respx_mock.post(success_url).mock(return_value=Response(status_code=200, text="OK"))

    with CheckTrap(test_client, uuid="test"):
        pass


@pytest.mark.respx
def test_check_trap_sync_failed_ping(respx_mock, test_client):
    start_url = urljoin(test_client._ping_url, "test/start")
    respx_mock.post(start_url).mock(return_value=Response(status_code=444, text="OK"))
    with pytest.raises(PingFailedError):
        with CheckTrap(test_client, uuid="test"):
            pass


@pytest.mark.respx
def test_check_trap_sync_exception(respx_mock, test_client):
    start_url = urljoin(test_client._ping_url, "test/start")
    respx_mock.post(start_url).mock(return_value=Response(status_code=200, text="OK"))
    fail_url = urljoin(test_client._ping_url, "test/fail")
    respx_mock.post(fail_url).mock(return_value=Response(status_code=200, text="OK"))
    with pytest.raises(Exception):
        with CheckTrap(test_client, uuid="test"):
            raise Exception("Exception")


@pytest.mark.asyncio
@pytest.mark.respx
async def test_check_trap_async(respx_mock, test_async_client):
    start_url = urljoin(test_async_client._ping_url, "test/start")
    respx_mock.post(start_url).mock(return_value=Response(status_code=200, text="OK"))
    success_url = urljoin(test_async_client._ping_url, "test")
    respx_mock.post(success_url).mock(return_value=Response(status_code=200, text="OK"))

    async with CheckTrap(test_async_client, uuid="test"):
        pass


@pytest.mark.asyncio
@pytest.mark.respx
async def test_check_trap_async_failed_ping(respx_mock, test_async_client):
    start_url = urljoin(test_async_client._ping_url, "test/start")
    respx_mock.post(start_url).mock(return_value=Response(status_code=444, text="OK"))
    with pytest.raises(PingFailedError):
        async with CheckTrap(test_async_client, uuid="test"):
            pass


@pytest.mark.asyncio
@pytest.mark.respx
async def test_check_trap_async_exception(respx_mock, test_async_client):
    start_url = urljoin(test_async_client._ping_url, "test/start")
    respx_mock.post(start_url).mock(return_value=Response(status_code=200, text="OK"))
    fail_url = urljoin(test_async_client._ping_url, "test/fail")
    respx_mock.post(fail_url).mock(return_value=Response(status_code=200, text="OK"))

    with pytest.raises(Exception):
        async with CheckTrap(test_async_client, uuid="test"):
            raise Exception("Exception")


@pytest.mark.asyncio
async def test_check_trap_wrong_client_error(test_client, test_async_client):
    with pytest.raises(WrongClientError):
        async with CheckTrap(test_client, uuid="test"):
            pass

    with pytest.raises(WrongClientError):
        with CheckTrap(test_async_client, uuid="test"):
            pass


def test_check_trap_no_uuid_or_slug(test_client):
    with pytest.raises(Exception) as exc:
        with CheckTrap(test_client):
            pass
        assert str(exc) == "Must pass a slug or an uuid"
