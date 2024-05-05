import pytest
from pydantic import ValidationError

from healthchecks_io.schemas import checks


def test_check_from_api_result(fake_check_api_result, fake_check_ro_api_result):
    check = checks.Check.from_api_result(fake_check_api_result)
    assert check.name == fake_check_api_result["name"]
    assert check.unique_key is None

    ro_check = checks.Check.from_api_result(fake_check_ro_api_result)
    assert ro_check.name == fake_check_ro_api_result["name"]
    assert ro_check.unique_key == fake_check_ro_api_result["unique_key"]


def test_check_validate_uuid(fake_check_api_result, fake_check_ro_api_result):
    check = checks.Check.from_api_result(fake_check_api_result)
    assert check.uuid == "8f57a84b-86c2-4246-8923-02f83d17604a"
    assert check.unique_key is None

    ro_check = checks.Check.from_api_result(fake_check_ro_api_result)
    assert ro_check.uuid is None


def test_check_create_validators():
    check_create = checks.CheckCreate(
        name="Test",
        tags="",
        desc="Test",
        schedule="* * * * *",
        tz="UTC",
        methods="POST",
        unique=["name"],
    )
    assert check_create.schedule == "* * * * *"

    # test validate_schedule
    with pytest.raises(ValidationError):
        check_create = checks.CheckCreate(name="Test", tags="", desc="Test", schedule="no good")

    # test validate_tz
    with pytest.raises(ValidationError):
        check_create = checks.CheckCreate(name="Test", tags="", desc="Test", tz="no good")

    # test validate_methods
    with pytest.raises(ValidationError):
        check_create = checks.CheckCreate(name="Test", tags="", desc="Test", methods="no good")

    # test validate_unique
    with pytest.raises(ValidationError):
        check_create = checks.CheckCreate(name="Test", tags="", desc="Test", unique=["no good"])


def test_check_pings_from_api():
    ping = {
        "type": "success",
        "date": "2020-06-09T14:51:06.113073+00:00",
        "n": 4,
        "scheme": "http",
        "remote_addr": "192.0.2.0",
        "method": "GET",
        "ua": "curl/7.68.0",
        "duration": 2.896736,
    }
    this_ping = checks.CheckPings.from_api_result(ping)
    assert this_ping.type == ping["type"]
    assert this_ping.duration == ping["duration"]
