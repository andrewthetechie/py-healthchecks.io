"""An async healthchecks.io client."""
import asyncio
from typing import Dict
from typing import List
from typing import Optional

from httpx import AsyncClient as HTTPXAsyncClient

from ._abstract import AbstractClient
from healthchecks_io import VERSION
from healthchecks_io.schemas import badges
from healthchecks_io.schemas import checks
from healthchecks_io.schemas import integrations


class AsyncClient(AbstractClient):
    """A Healthchecks.io client implemented using httpx's Async methods."""

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://healthchecks.io/api/",
        api_version: int = 1,
        client: Optional[HTTPXAsyncClient] = None,
    ) -> None:
        """An AsyncClient can be used in code using asyncio to work with the Healthchecks.io api.

        Args:
            api_key (str): Healthchecks.io API key
            api_url (str): API URL. Defaults to "https://healthchecks.io/api/".
            api_version (int): Versiopn of the api to use. Defaults to 1.
            client (Optional[HTTPXAsyncClient], optional): A httpx.Asyncclient. If not
                passed in, one will be created for this object. Defaults to None.
        """
        self._client: HTTPXAsyncClient = (
            HTTPXAsyncClient() if client is None else client
        )
        super().__init__(api_key=api_key, api_url=api_url, api_version=api_version)
        self._client.headers["X-Api-Key"] = self._api_key
        self._client.headers["user-agent"] = f"py-healthchecks.io-async/{VERSION}"
        self._client.headers["Content-type"] = "application/json"

    def _finalizer_method(self) -> None:
        """Calls _afinalizer_method from a sync context to work with weakref.finalizer."""
        asyncio.run(self._afinalizer_method())

    async def _afinalizer_method(self) -> None:
        """Finalizer coroutine that closes our client connections."""
        await self._client.aclose()

    async def get_checks(self, tags: Optional[List[str]] = None) -> List[checks.Check]:
        """Get a list of checks from the healthchecks api.

        Args:
            tags (Optional[List[str]], optional): Filters the checks and returns only
                the checks that are tagged with the specified value. Defaults to None.

        Raises:
            HCAPIAuthError: When the API returns a 401, indicates an api key issue
            HCAPIError: When the API returns anything other than a 200 or 401

        Returns:
            List[checks.Check]: [description]
        """
        request_url = self._get_api_request_url("checks/")
        if tags is not None:
            for tag in tags:
                request_url = self._add_url_params(
                    request_url, {"tag": tag}, replace=False
                )

        response = self.check_response(await self._client.get(request_url))

        return [
            checks.Check.from_api_result(check_data)
            for check_data in response.json()["checks"]
        ]

    async def get_check(self, check_id: str) -> checks.Check:
        """Get a single check by id.

        check_id can either be a check uuid if using a read/write api key
        or a unique key if using a read only api key.

        Args:
            check_id (str): check's uuid or unique id

        Returns:
            checks.Check: the check

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404

        """
        request_url = self._get_api_request_url(f"checks/{check_id}")
        response = self.check_response(await self._client.get(request_url))
        return checks.Check.from_api_result(response.json())

    async def pause_check(self, check_id: str) -> checks.Check:
        """Disables monitoring for a check without removing it.

        The check goes into a "paused" state.
        You can resume monitoring of the check by pinging it.

        check_id must be a uuid, not a unique id

        Args:
            check_id (str): check's uuid

        Returns:
            checks.Check: the check just paused

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404

        """
        request_url = self._get_api_request_url(f"checks/{check_id}/pause")
        response = self.check_response(await self._client.post(request_url, data={}))
        return checks.Check.from_api_result(response.json())

    async def delete_check(self, check_id: str) -> checks.Check:
        """Permanently deletes the check from the user's account.

        check_id must be a uuid, not a unique id

        Args:
            check_id (str): check's uuid

        Returns:
            checks.Check: the check just deleted

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404

        """
        request_url = self._get_api_request_url(f"checks/{check_id}")
        response = self.check_response(await self._client.delete(request_url))
        return checks.Check.from_api_result(response.json())

    async def get_check_pings(self, check_id: str) -> List[checks.CheckPings]:
        """Returns a list of pings this check has received.

        This endpoint returns pings in reverse order (most recent first),
        and the total number of returned pings depends on the account's
        billing plan: 100 for free accounts, 1000 for paid accounts.

        Args:
            check_id (str): check's uuid

        Returns:
            List[checks.CheckPings]: list of pings this check has received

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404

        """
        request_url = self._get_api_request_url(f"checks/{check_id}/pings/")
        response = self.check_response(await self._client.get(request_url))
        return [
            checks.CheckPings.from_api_result(check_data)
            for check_data in response.json()["pings"]
        ]

    async def get_check_flips(
        self,
        check_id: str,
        seconds: Optional[int] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> List[checks.CheckStatuses]:
        """Returns a list of "flips" this check has experienced.

        A flip is a change of status (from "down" to "up," or from "up" to "down").

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404
            BadAPIRequestError: Raised when status_code is 400

        Args:
            check_id (str): check uuid
            seconds (Optional[int], optional): Returns the flips from the last value seconds. Defaults to None.
            start (Optional[int], optional): Returns flips that are newer than the specified UNIX timestamp.. Defaults to None.
            end (Optional[int], optional): Returns flips that are older than the specified UNIX timestamp.. Defaults to None.

        Returns:
            List[checks.CheckStatuses]: List of status flips for this check

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
        return [checks.CheckStatuses(**status_data) for status_data in response.json()]

    async def get_integrations(self) -> List[Optional[integrations.Integration]]:
        """Returns a list of integrations belonging to the project.

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx

        Returns:
            List[Optional[integrations.Integration]]: List of integrations for the project

        """
        request_url = self._get_api_request_url("channels/")
        response = self.check_response(await self._client.get(request_url))
        return [
            integrations.Integration.from_api_result(integration_dict)
            for integration_dict in response.json()["channels"]
        ]

    async def get_badges(self) -> Dict[str, badges.Badges]:
        """Returns a dict of all tags in the project, with badge URLs for each tag.

        Healthchecks.io provides badges in a few different formats:
        svg: returns the badge as a SVG document.
        json: returns a JSON document which you can use to generate a custom badge yourself.
        shields: returns JSON in a Shields.io compatible format.
        In addition, badges have 2-state and 3-state variations:

        svg, json, shields: reports two states: "up" and "down". It considers any checks in the grace period as still "up".
        svg3, json3, shields3: reports three states: "up", "late", and "down".

        The response includes a special * entry: this pseudo-tag reports the overal status
        of all checks in the project.

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx

        Returns:
            Dict[str, badges.Badges]: Dictionary of all tags in the project with badges
        """
        request_url = self._get_api_request_url("badges/")
        url = await self._client.get(request_url)
        response = self.check_response(url)
        return {
            key: badges.Badges.from_api_result(item)
            for key, item in response.json()["badges"].items()
        }
