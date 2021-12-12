from datetime import datetime
from typing import Dict
from typing import Union

import pytest

from healthchecks_io import AsyncClient
from healthchecks_io import Client
from healthchecks_io.client._abstract import AbstractClient
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


client_kwargs = {
    "api_key": "test",
    "api_url": "https://localhost/api",
    "ping_url": "https://localhost/ping",
    "ping_key": "1234",
}


@pytest.fixture
def test_async_client():
    """An AsyncClient for testing, set to a nonsense url so we aren't pinging healtchecks."""
    yield AsyncClient(**client_kwargs)


@pytest.fixture
def test_client():
    """A Client for testing, set to a nonsense url so we aren't pinging healtchecks."""
    yield Client(**client_kwargs)


@pytest.fixture
def test_abstract_client():
    AbstractClient.__abstractmethods__ = set()
    yield AbstractClient(**client_kwargs)


@pytest.fixture
def fake_check_pings_api_result():
    yield [
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
    yield [
        {"timestamp": "2020-03-23T10:18:23+00:00", "up": 1},
        {"timestamp": "2020-03-23T10:17:15+00:00", "up": 0},
        {"timestamp": "2020-03-23T10:16:18+00:00", "up": 1},
    ]


@pytest.fixture
def fake_integrations_api_result():
    yield {
        "channels": [
            {
                "id": "4ec5a071-2d08-4baa-898a-eb4eb3cd6941",
                "name": "My Work Email",
                "kind": "email",
            },
            {
                "id": "746a083e-f542-4554-be1a-707ce16d3acc",
                "name": "My Phone",
                "kind": "sms",
            },
        ]
    }


@pytest.fixture
def fake_badges_api_result():
    yield {
        "badges": {
            "backup": {
                "svg": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M-2/backup.svg",
                "svg3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M/backup.svg",
                "json": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M-2/backup.json",
                "json3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M/backup.json",
                "shields": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M-2/backup.shields",
                "shields3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M/backup.shields",
            },
            "db": {
                "svg": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/99MuQaKm-2/db.svg",
                "svg3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/99MuQaKm/db.svg",
                "json": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/99MuQaKm-2/db.json",
                "json3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/99MuQaKm/db.json",
                "shields": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/99MuQaKm-2/db.shields",
                "shields3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/99MuQaKm/db.shields",
            },
            "prod": {
                "svg": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/1TEhqie8-2/prod.svg",
                "svg3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/1TEhqie8/prod.svg",
                "json": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/1TEhqie8-2/prod.json",
                "json3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/1TEhqie8/prod.json",
                "shields": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/1TEhqie8-2/prod.shields",
                "shields3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/1TEhqie8/prod.shields",
            },
            "*": {
                "svg": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/9X7kcZoe-2.svg",
                "svg3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/9X7kcZoe.svg",
                "json": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/9X7kcZoe-2.json",
                "json3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/9X7kcZoe.json",
                "shields": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/9X7kcZoe-2.shields",
                "shields3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/9X7kcZoe.shields",
            },
        }
    }
