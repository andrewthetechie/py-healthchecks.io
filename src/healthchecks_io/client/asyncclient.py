"""An async healthchecks.io client."""
import asyncio
from typing import List
from typing import Optional

from httpx import AsyncClient as HTTPXAsyncClient

from ._abstract import AbstractClient
from .exceptions import HCAPIAuthError, CheckNotFoundError
from .exceptions import HCAPIError
from healthchecks_io import VERSION
from healthchecks_io.schemas import checks


class AsyncClient(AbstractClient):
    """A Healthchecks.io client implemented using httpx's Async methods."""

    def __init__(
        self,
        api_key: str,
        api_url: Optional[str] = "https://healthchecks.io/api/",
        api_version: Optional[int] = 1,
        client: Optional[HTTPXAsyncClient] = None,
    ) -> None:
        """An AsyncClient can be used in code using asyncio to work with the Healthchecks.io api.

        Args:
            api_key (str): Healthchecks.io API key
            api_url (Optional[str], optional): API URL. Defaults to "https://healthchecks.io/api/".
            api_version (Optional[int], optional): Versiopn of the api to use. Defaults to 1.
            client (Optional[HTTPXAsyncClient], optional): A httpx.Asyncclient. If not
                passed in, one will be created for this object. Defaults to None.
        """
        if client is None:
            client = HTTPXAsyncClient()
        super().__init__(
            api_key=api_key, api_url=api_url, api_version=api_version, client=client
        )
        self._client.headers["X-Api-Key"] = self._api_key
        self._client.headers["user-agent"] = f"py-healthchecks.io/{VERSION}"
        self._client.headers["Content-type"] = "application/json"

    def _finalizer_method(self):
        """Calls _afinalizer_method from a sync context to work with weakref.finalizer."""
        asyncio.run(self._afinalizer_method())

    async def _afinalizer_method(self):
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
            CheckNotFoundError: when no check with check_id is found
        """
        request_url = self._get_api_request_url(f"checks/{check_id}")
        response = self.check_response(await self._client.get(request_url))
        if response.status_code == 404:
            raise CheckNotFoundError(f"{check_id} not found at {request_url}")
        return checks.Check.from_api_result(response.json())

