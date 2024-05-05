"""An async healthchecks.io client."""

import asyncio
from types import TracebackType
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from httpx import AsyncClient as HTTPXAsyncClient

from ._abstract import AbstractClient
from healthchecks_io import __version__ as client_version
from healthchecks_io.schemas import Badges
from healthchecks_io.schemas import Check
from healthchecks_io.schemas import CheckCreate
from healthchecks_io.schemas import CheckPings
from healthchecks_io.schemas import CheckStatuses
from healthchecks_io.schemas import Integration


class AsyncClient(AbstractClient):
    """A Healthchecks.io client implemented using httpx's Async methods."""

    def __init__(
        self,
        api_key: str = "",
        ping_key: str = "",
        api_url: str = "https://healthchecks.io/api/",
        ping_url: str = "https://hc-ping.com/",
        api_version: int = 1,
        client: Optional[HTTPXAsyncClient] = None,
    ) -> None:
        """An AsyncClient can be used in code using asyncio to work with the Healthchecks.io api.

        Args:
            api_key (str): Healthchecks.io API key. Defaults to an empty string.
            ping_key (str): Healthchecks.io Ping key. Defaults to an empty string.
            api_url (str): API URL. Defaults to "https://healthchecks.io/api/".
            ping_url (str): Ping API url. Defaults to "https://hc-ping.com/"
            api_version (int): Versiopn of the api to use. Defaults to 1.
            client (Optional[HTTPXAsyncClient], optional): A httpx.Asyncclient. If not
                passed in, one will be created for this object. Defaults to None.
        """
        self._client: HTTPXAsyncClient = HTTPXAsyncClient() if client is None else client
        super().__init__(
            api_key=api_key,
            ping_key=ping_key,
            api_url=api_url,
            ping_url=ping_url,
            api_version=api_version,
        )
        self._client.headers["X-Api-Key"] = self._api_key
        self._client.headers["user-agent"] = f"py-healthchecks.io-async/{client_version}"
        self._client.headers["Content-type"] = "application/json"

    async def __aenter__(self) -> "AsyncClient":
        """Context manager entrance.

        Returns:
            AsyncClient: returns this client as a context manager
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Context manager exit."""
        await self._afinalizer_method()

    def _finalizer_method(self) -> None:
        """Calls _afinalizer_method from a sync context to work with weakref.finalizer."""
        asyncio.run(self._afinalizer_method())

    async def _afinalizer_method(self) -> None:
        """Finalizer coroutine that closes our client connections."""
        await self._client.aclose()

    async def create_check(self, new_check: CheckCreate) -> Check:
        """Creates a new check and returns it.

        With this API call, you can create both Simple and Cron checks:
        * To create a Simple check, specify the timeout parameter.
        * To create a Cron check, specify the schedule and tz parameters.

        Args:
            new_check (CheckCreate): New check you are wanting to create

        Returns:
            Check: check that was just created
        """
        request_url = self._get_api_request_url("checks/")
        response = self.check_response(await self._client.post(request_url, json=new_check.dict(exclude_none=True)))
        return Check.from_api_result(response.json())

    async def update_check(self, uuid: str, update_check: CheckCreate) -> Check:
        """Updates an existing check.

        If you omit any parameter in update_check, Healthchecks.io will leave
        its value unchanged.

        Args:
            uuid (str): UUID for the check to update
            update_check (CheckCreate): Check values you want to update

        Returns:
            Check: check that was just updated
        """
        request_url = self._get_api_request_url(f"checks/{uuid}")
        response = self.check_response(
            await self._client.post(
                request_url,
                json=update_check.dict(exclude_unset=True, exclude_none=True),
            )
        )
        return Check.from_api_result(response.json())

    async def get_checks(self, tags: Optional[List[str]] = None) -> List[Check]:
        """Get a list of checks from the healthchecks api.

        Args:
            tags (Optional[List[str]], optional): Filters the checks and returns only
                the checks that are tagged with the specified value. Defaults to None.

        Raises:
            HCAPIAuthError: When the API returns a 401, indicates an api key issue
            HCAPIError: When the API returns anything other than a 200 or 401
            HCAPIRateLimitError: Raised when status code is 429


        Returns:
            List[Check]: [description]
        """
        request_url = self._get_api_request_url("checks/")
        if tags is not None:
            for tag in tags:
                request_url = self._add_url_params(request_url, {"tag": tag}, replace=False)

        response = self.check_response(await self._client.get(request_url))

        return [Check.from_api_result(check_data) for check_data in response.json()["checks"]]

    async def get_check(self, check_id: str) -> Check:
        """Get a single check by id.

        check_id can either be a check uuid if using a read/write api key
        or a unique key if using a read only api key.

        Args:
            check_id (str): check's uuid or unique id

        Returns:
            Check: the check

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404
            HCAPIRateLimitError: Raised when status code is 429


        """
        request_url = self._get_api_request_url(f"checks/{check_id}")
        response = self.check_response(await self._client.get(request_url))
        return Check.from_api_result(response.json())

    async def pause_check(self, check_id: str) -> Check:
        """Disables monitoring for a check without removing it.

        The check goes into a "paused" state.
        You can resume monitoring of the check by pinging it.

        check_id must be a uuid, not a unique id

        Args:
            check_id (str): check's uuid

        Returns:
            Check: the check just paused

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404

        """
        request_url = self._get_api_request_url(f"checks/{check_id}/pause")
        response = self.check_response(await self._client.post(request_url, data={}))
        return Check.from_api_result(response.json())

    async def delete_check(self, check_id: str) -> Check:
        """Permanently deletes the check from the user's account.

        check_id must be a uuid, not a unique id

        Args:
            check_id (str): check's uuid

        Returns:
            Check: the check just deleted

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404
            HCAPIRateLimitError: Raised when status code is 429

        """
        request_url = self._get_api_request_url(f"checks/{check_id}")
        response = self.check_response(await self._client.delete(request_url))
        return Check.from_api_result(response.json())

    async def get_check_pings(self, check_id: str) -> List[CheckPings]:
        """Returns a list of pings this check has received.

        This endpoint returns pings in reverse order (most recent first),
        and the total number of returned pings depends on the account's
        billing plan: 100 for free accounts, 1000 for paid accounts.

        Args:
            check_id (str): check's uuid

        Returns:
            List[CheckPings]: list of pings this check has received

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404
            HCAPIRateLimitError: Raised when status code is 429


        """
        request_url = self._get_api_request_url(f"checks/{check_id}/pings/")
        response = self.check_response(await self._client.get(request_url))
        return [CheckPings.from_api_result(check_data) for check_data in response.json()["pings"]]

    async def get_check_flips(
        self,
        check_id: str,
        seconds: Optional[int] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> List[CheckStatuses]:
        """Returns a list of "flips" this check has experienced.

        A flip is a change of status (from "down" to "up," or from "up" to "down").

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404
            BadAPIRequestError: Raised when status_code is 400
            HCAPIRateLimitError: Raised when status code is 429


        Args:
            check_id (str): check uuid
            seconds (Optional[int], optional): Returns the flips from the last value seconds. Defaults to None.
            start (Optional[int], optional): Returns flips that are newer than the specified UNIX timestamp.
                Defaults to None.
            end (Optional[int], optional): Returns flips that are older than the specified UNIX timestamp.
                Defaults to None.

        Returns:
            List[CheckStatuses]: List of status flips for this check

        """
        params = dict()
        if seconds is not None and seconds >= 0:
            params["seconds"] = seconds
        if start is not None and start >= 0:
            params["start"] = start
        if end is not None and end >= 0:
            params["end"] = end

        request_url = self._get_api_request_url(f"checks/{check_id}/flips/", params)
        response = self.check_response(await self._client.get(request_url))
        return [CheckStatuses(**status_data) for status_data in response.json()]

    async def get_integrations(self) -> List[Optional[Integration]]:
        """Returns a list of integrations belonging to the project.

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            HCAPIRateLimitError: Raised when status code is 429

        Returns:
            List[Optional[Integration]]: List of integrations for the project

        """
        request_url = self._get_api_request_url("channels/")
        response = self.check_response(await self._client.get(request_url))
        return [Integration.from_api_result(integration_dict) for integration_dict in response.json()["channels"]]

    async def get_badges(self) -> Dict[str, Badges]:
        """Returns a dict of all tags in the project, with badge URLs for each tag.

        Healthchecks.io provides badges in a few different formats:
        svg: returns the badge as a SVG document.
        json: returns a JSON document which you can use to generate a custom badge yourself.
        shields: returns JSON in a Shields.io compatible format.
        In addition, badges have 2-state and 3-state variations:

        svg, json, shields: reports two states: "up" and "down". It considers any checks in the grace period
        as still "up".
        svg3, json3, shields3: reports three states: "up", "late", and "down".

        The response includes a special * entry: this pseudo-tag reports the overal status
        of all checks in the project.

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            HCAPIRateLimitError: Raised when status code is 429

        Returns:
            Dict[str, Badges]: Dictionary of all tags in the project with badges
        """
        request_url = self._get_api_request_url("badges/")
        response = self.check_response(await self._client.get(request_url))
        return {key: Badges.from_api_result(item) for key, item in response.json()["badges"].items()}

    async def success_ping(self, uuid: str = "", slug: str = "", data: str = "") -> Tuple[bool, str]:
        """Signals to Healthchecks.io that a job has completed successfully.

        Can also be used to indicate a continuously running process is still running and healthy.

        Can take a uuid or a slug. If you call with a slug, you much have a
        ping key set.

        Check's slug is not guaranteed to be unique. If multiple checks in the
        project have the same name, they also have the same slug. If you make
        a Pinging API request using a non-unique slug, Healthchecks.io will
        return the "409 Conflict" HTTP status code and ignore the request.

        Args:
            uuid (str): Check's UUID. Defaults to "".
            slug (str):  Check's Slug. Defaults to "".
            data (str): Text data to append to this check. Defaults to "".

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404 or response text has "not found" in it
            BadAPIRequestError: Raised when status_code is 400, or if you pass a uuid and a slug, or if
                pinging by a slug and do not have a ping key set
            HCAPIRateLimitError: Raised when status code is 429 or response text has "rate limited" in it
            NonUniqueSlugError: Raused when status code is 409.

        Returns:
            Tuple[bool, str]: success (true or false) and the response text
        """
        ping_url = self._get_ping_url(uuid, slug, "")
        response = self.check_ping_response(await self._client.post(ping_url, content=data))
        return (True if response.status_code == 200 else False, response.text)

    async def start_ping(self, uuid: str = "", slug: str = "", data: str = "") -> Tuple[bool, str]:
        """Sends a "job has started!" message to Healthchecks.io.

        Sending a "start" signal is optional, but it enables a few extra features:
        * Healthchecks.io will measure and display job execution times
        * Healthchecks.io will detect if the job runs longer than its configured grace time

        Can take a uuid or a slug. If you call with a slug, you much have a
        ping key set.

        Check's slug is not guaranteed to be unique. If multiple checks in the
        project have the same name, they also have the same slug. If you make
        a Pinging API request using a non-unique slug, Healthchecks.io will
        return the "409 Conflict" HTTP status code and ignore the request.

        Args:
            uuid (str): Check's UUID. Defaults to "".
            slug (str): Check's Slug. Defaults to "".
            data (str): Text data to append to this check. Defaults to "".

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404 or response text has "not found" in it
            BadAPIRequestError: Raised when status_code is 400, or if you pass a uuid and a slug, or if
                pinging by a slug and do not have a ping key set
            HCAPIRateLimitError: Raised when status code is 429 or response text has "rate limited" in it
            NonUniqueSlugError: Raused when status code is 409.

        Returns:
            Tuple[bool, str]: success (true or false) and the response text
        """
        ping_url = self._get_ping_url(uuid, slug, "/start")
        response = self.check_ping_response(await self._client.post(ping_url, content=data))
        return (True if response.status_code == 200 else False, response.text)

    async def fail_ping(self, uuid: str = "", slug: str = "", data: str = "") -> Tuple[bool, str]:
        """Signals to Healthchecks.io that the job has failed.

        Actively signaling a failure minimizes the delay from your monitored service failing to you receiving an alert.

        Can take a uuid or a slug. If you call with a slug, you much have a
        ping key set.

        Check's slug is not guaranteed to be unique. If multiple checks in the
        project have the same name, they also have the same slug. If you make
        a Pinging API request using a non-unique slug, Healthchecks.io will
        return the "409 Conflict" HTTP status code and ignore the request.

        Args:
            uuid (str): Check's UUID. Defaults to "".
            slug (str): Check's Slug. Defaults to "".
            data (str): Text data to append to this check. Defaults to "".

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404 or response text has "not found" in it
            BadAPIRequestError: Raised when status_code is 400, or if you pass a uuid and a slug, or if
                pinging by a slug and do not have a ping key set
            HCAPIRateLimitError: Raised when status code is 429 or response text has "rate limited" in it
            NonUniqueSlugError: Raused when status code is 409.

        Returns:
            Tuple[bool, str]: success (true or false) and the response text
        """
        ping_url = self._get_ping_url(uuid, slug, "/fail")
        response = self.check_ping_response(await self._client.post(ping_url, content=data))
        return (True if response.status_code == 200 else False, response.text)

    async def exit_code_ping(self, exit_code: int, uuid: str = "", slug: str = "", data: str = "") -> Tuple[bool, str]:
        """Signals to Healthchecks.io that the job has failed.

        Actively signaling a failure minimizes the delay from your monitored service failing to you receiving an alert.

        Can take a uuid or a slug. If you call with a slug, you much have a
        ping key set.

        Check's slug is not guaranteed to be unique. If multiple checks in the
        project have the same name, they also have the same slug. If you make
        a Pinging API request using a non-unique slug, Healthchecks.io will
        return the "409 Conflict" HTTP status code and ignore the request.

        Args:
            exit_code (int): Exit code to sent, int from 0 to 255
            uuid (str): Check's UUID. Defaults to "".
            slug (str): Check's Slug. Defaults to "".
            data (str): Text data to append to this check. Defaults to "".

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404 or response text has "not found" in it
            BadAPIRequestError: Raised when status_code is 400, or if you pass a uuid and a slug, or if
                pinging by a slug and do not have a ping key set
            HCAPIRateLimitError: Raised when status code is 429 or response text has "rate limited" in it
            NonUniqueSlugError: Raused when status code is 409.

        Returns:
            Tuple[bool, str]: success (true or false) and the response text
        """
        ping_url = self._get_ping_url(uuid, slug, f"/{exit_code}")
        response = self.check_ping_response(await self._client.post(ping_url, content=data))
        return (True if response.status_code == 200 else False, response.text)
