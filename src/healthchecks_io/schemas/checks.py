"""Schemas for checks.

https://healthchecks.io/docs/api/
"""

from datetime import datetime
from pathlib import PurePath
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlparse

import pytz
from croniter import croniter
from pydantic import field_validator, BaseModel, ValidationInfo
from pydantic import Field


class Check(BaseModel):
    """Schema for a check object, either from a readonly api request or a rw api request."""

    unique_key: Optional[str] = None
    name: str
    slug: str
    tags: Optional[str] = None
    desc: Optional[str] = None
    grace: int
    n_pings: int
    status: str
    last_ping: Optional[datetime] = None
    next_ping: Optional[datetime] = None
    manual_resume: bool
    methods: Optional[str] = None
    # healthchecks.io's api doesn't return a scheme so we cant use Pydantic AnyUrl here
    ping_url: Optional[str] = None
    update_url: Optional[str] = None
    pause_url: Optional[str] = None
    channels: Optional[str] = None
    timeout: Optional[int] = None
    uuid: Optional[str] = Field(default=None, validate_default=True)

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:  # noqa: B902
        """Tries to set the uuid from the ping_url.

        Will return none if a read only token is used because it cannot retrieve the UUID of a check
        """
        if value is None and info.data.get("ping_url", None) is not None:
            # url is like healthchecks.io/ping/8f57b84b-86c2-4546-8923-03f83d27604a, so we want just the
            # UUID off the end
            # Parse the url, grab the path and then just get the name using pathlib
            path = PurePath(str(urlparse(info.data.get("ping_url")).path))
            return path.name
        return value

    @classmethod
    def from_api_result(cls, check_dict: Dict[str, Any]) -> "Check":
        """Converts a dictionary from the healthchecks api into an Check object."""
        return cls(**check_dict)


class CheckCreate(BaseModel):
    """Pydantic object for creating a check."""

    name: Optional[str] = Field("", description="Name of the check")
    tags: Optional[str] = Field("", description="String separated list of tags to apply")
    desc: Optional[str] = Field("", description="Description of the check")
    timeout: Optional[int] = Field(
        86400,
        description="The expected period of this check in seconds.",
        gte=60,
        lte=31536000,
    )
    grace: Optional[int] = Field(
        3600,
        description="The grace period for this check in seconds.",
        gte=60,
        lte=31536000,
    )
    schedule: Optional[str] = Field(
        None,
        description="A cron expression defining this check's schedule. "
        "If you specify both timeout and schedule parameters, "
        "Healthchecks.io will create a Cron check and ignore the "
        "timeout value.",
    )
    tz: Optional[str] = Field(
        "UTC",
        description="Server's timezone. This setting only has an effect " "in combination with the schedule parameter.",
    )
    manual_resume: Optional[bool] = Field(
        False,
        description="Controls whether a paused check automatically resumes "
        "when pinged (the default) or not. If set to false, a paused "
        "check will leave the paused state when it receives a ping. "
        "If set to true, a paused check will ignore pings and stay "
        "paused until you manually resume it from the web dashboard.",
    )
    methods: Optional[str] = Field(
        "",
        description="Specifies the allowed HTTP methods for making "
        "ping requests. Must be one of the two values: an empty "
        "string or POST. Set this field to an empty string to "
        "allow HEAD, GET, and POST requests. Set this field to "
        "POST to allow only POST requests.",
    )
    channels: Optional[str] = Field(
        None,
        description="By default, this API call assigns no integrations"
        "to the newly created check. By default, this API call "
        "assigns no integrations to the newly created check. "
        "To assign specific integrations, use a comma-separated list "
        "of integration UUIDs.",
    )
    unique: Optional[List[Optional[str]]] = Field(
        [],
        description="Enables upsert functionality. Before creating a check, "
        "Healthchecks.io looks for existing checks, filtered by fields listed "
        "in unique. If Healthchecks.io does not find a matching check, it "
        "creates a new check and returns it with the HTTP status code 201 "
        "If Healthchecks.io finds a matching check, it updates the existing "
        "check and returns it with HTTP status code 200. The accepted values "
        "for the unique field are name, tags, timeout, and grace.",
    )

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, value: str) -> str:
        """Validates that the schedule is a valid cron expression."""
        if not croniter.is_valid(value):
            raise ValueError("Schedule is not a valid cron expression")
        return value

    @field_validator("tz")
    @classmethod
    def validate_tz(cls, value: str) -> str:
        """Validates that the timezone is a valid timezone string."""
        if value not in pytz.all_timezones:
            raise ValueError("Tz is not a valid timezone")
        return value

    @field_validator("methods")
    @classmethod
    def validate_methods(cls, value: str) -> str:
        """Validate that methods."""
        if value not in ("", "POST"):
            raise ValueError("Methods is invalid, it should be either an empty string or POST")
        return value

    @field_validator("unique")
    @classmethod
    def validate_unique(cls, value: List[Optional[str]]) -> List[Optional[str]]:
        """Validate unique list."""
        for unique in value:
            if unique not in ("name", "tags", "timeout", "grace"):
                raise ValueError(
                    "Unique is not valid. Unique can only be name, tags, timeout, and grace or an empty list"
                )
        return value


class CheckUpdate(CheckCreate):
    """Pydantic object for updating a check."""

    name: Optional[str] = Field(None, description="Name of the check")
    tags: Optional[str] = Field(None, description="String separated list of tags to apply")
    timeout: Optional[int] = Field(
        None,
        description="The expected period of this check in seconds.",
        gte=60,
        lte=31536000,
    )
    grace: Optional[int] = Field(
        None,
        description="The grace period for this check in seconds.",
        gte=60,
        lte=31536000,
    )
    schedule: Optional[str] = Field(
        None,
        description="A cron expression defining this check's schedule. "
        "If you specify both timeout and schedule parameters, "
        "Healthchecks.io will create a Cron check and ignore the "
        "timeout value.",
    )
    tz: Optional[str] = Field(
        None,
        description="Server's timezone. This setting only has an effect " "in combination with the schedule parameter.",
    )
    manual_resume: Optional[bool] = Field(
        None,
        description="Controls whether a paused check automatically resumes "
        "when pinged (the default) or not. If set to false, a paused "
        "check will leave the paused state when it receives a ping. "
        "If set to true, a paused check will ignore pings and stay "
        "paused until you manually resume it from the web dashboard.",
    )
    methods: Optional[str] = Field(
        None,
        description="Specifies the allowed HTTP methods for making "
        "ping requests. Must be one of the two values: an empty "
        "string or POST. Set this field to an empty string to "
        "allow HEAD, GET, and POST requests. Set this field to "
        "POST to allow only POST requests.",
    )
    channels: Optional[str] = Field(
        None,
        description="By default, this API call assigns no integrations"
        "to the newly created check. By default, this API call "
        "assigns no integrations to the newly created check. "
        "To assign specific integrations, use a comma-separated list "
        "of integration UUIDs.",
    )
    unique: Optional[List[Optional[str]]] = Field(
        None,
        description="Enables upsert functionality. Before creating a check, "
        "Healthchecks.io looks for existing checks, filtered by fields listed "
        "in unique. If Healthchecks.io does not find a matching check, it "
        "creates a new check and returns it with the HTTP status code 201 "
        "If Healthchecks.io finds a matching check, it updates the existing "
        "check and returns it with HTTP status code 200. The accepted values "
        "for the unique field are name, tags, timeout, and grace.",
    )


class CheckPings(BaseModel):
    """A Pydantic schema for a check's Pings."""

    type: str
    date: datetime
    number_of_pings: int
    scheme: str
    remote_addr: str
    method: str
    user_agent: str
    duration: Optional[float] = None

    @classmethod
    def from_api_result(cls, ping_dict: Dict[str, Union[str, int, datetime]]) -> "CheckPings":
        """Converts a dictionary from the healthchecks api into a CheckPings object."""
        ping_dict["number_of_pings"] = ping_dict["n"]
        ping_dict["user_agent"] = ping_dict["ua"]
        return cls(**ping_dict)


class CheckStatuses(BaseModel):
    """A Pydantic schema for a check's Statuses."""

    timestamp: datetime
    up: int
