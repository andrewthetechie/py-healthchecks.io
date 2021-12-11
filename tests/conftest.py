from datetime import datetime
from typing import Dict
from typing import Union

import pytest

from healthchecks_io.client import AsyncClient
from healthchecks_io.schemas import checks


@pytest.fixture
def fake_check_api_result() -> Dict[str, Union[str, int]]:
    yield {
        "name": "Test Check",
        "slug": "Test Check",
        "tags": "test check",
        "desc": "Test Check",
        "grace": 43200,
        "n_pings": 76,
        "status": "up",
        "last_ping": "2021-12-03T12:30:16+00:00",
        "next_ping": "2021-12-06T12:30:16+00:00",
        "manual_resume": False,
        "methods": "",
        "ping_url": "testhc.io/ping/8f57a84b-86c2-4246-8923-02f83d17604a",
        "update_url": "testhc.io/api/v1/checks/8f57a84b-86c2-4246-8923-02f83d17604a",
        "pause_url": "testhc.io/api/v1/checks/8f57a84b-86c2-4246-8923-02f83d17604a/pause",
        "channels": "*",
        "timeout": 259200,
    }


@pytest.fixture
def fake_check_ro_api_result() -> Dict[str, Union[str, int]]:
    yield {
        "name": "Test Check",
        "slug": "Test Check",
        "tags": "Test Check",
        "desc": "Test Check",
        "grace": 600,
        "n_pings": 1,
        "status": "up",
        "last_ping": "2020-03-24T14:02:03+00:00",
        "next_ping": "2020-03-24T15:02:03+00:00",
        "manual_resume": False,
        "methods": "",
        "unique_key": "a6c7b0a8a66bed0df66abfdab3c77736861703ee",
        "timeout": 3600,
    }


@pytest.fixture
def fake_check() -> checks.Check:
    yield checks.Check(
        name="Test Check",
        slug="Test Check",
        tags="test check",
        desc="Test Check",
        grace=3600,
        n_pings=1,
        status="Test",
        last_ping=datetime.utcnow(),
        next_ping=datetime.utcnow(),
        manual_resume=False,
        ping_url="testurl.com/ping/test-uuid",
        update_url="testurl.com/api/v1/checks/test-uuid",
        pause_url="testurl.com/api/v1/checks/test-uuid/pause",
        channel="*",
        timeout=86400,
        uuid="test-uuid",
    )


@pytest.fixture
def fake_ro_check(fake_check: checks.Check):
    fake_check.unique_key = "test-unique-key"
    fake_check.uuid = None
    fake_check.ping_url = None
    fake_check.update_url = None
    fake_check.pause_url = None
    yield fake_check


@pytest.fixture
def test_async_client():
    """An AsyncClient for testing, set to a nonsense url so we aren't pinging healtchecks."""

    yield AsyncClient(api_key="test", api_url="https://localhost/api")


@pytest.fixture
def fake_check_pings_api_result():
    return [
        {
            "type": "success",
            "date": "2020-06-09T14:51:06.113073+00:00",
            "n": 4,
            "scheme": "http",
            "remote_addr": "192.0.2.0",
            "method": "GET",
            "ua": "curl/7.68.0",
            "duration": 2.896736,
        },
        {
            "type": "start",
            "date": "2020-06-09T14:51:03.216337+00:00",
            "n": 3,
            "scheme": "http",
            "remote_addr": "192.0.2.0",
            "method": "GET",
            "ua": "curl/7.68.0",
        },
        {
            "type": "success",
            "date": "2020-06-09T14:50:59.633577+00:00",
            "n": 2,
            "scheme": "http",
            "remote_addr": "192.0.2.0",
            "method": "GET",
            "ua": "curl/7.68.0",
            "duration": 2.997976,
        },
        {
            "type": "start",
            "date": "2020-06-09T14:50:56.635601+00:00",
            "n": 1,
            "scheme": "http",
            "remote_addr": "192.0.2.0",
            "method": "GET",
            "ua": "curl/7.68.0",
        },
    ]


@pytest.fixture
def fake_check_flips_api_result():
    return [
        {"timestamp": "2020-03-23T10:18:23+00:00", "up": 1},
        {"timestamp": "2020-03-23T10:17:15+00:00", "up": 0},
        {"timestamp": "2020-03-23T10:16:18+00:00", "up": 1},
    ]
