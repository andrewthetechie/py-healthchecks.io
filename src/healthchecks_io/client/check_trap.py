"""CheckTrap is a context manager to wrap around python code to communicate results to a Healthchecks check."""

from types import TracebackType
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from .async_client import AsyncClient
from .exceptions import PingFailedError
from .exceptions import WrongClientError
from .sync_client import Client


class CheckTrap:
    """CheckTrap is a context manager to wrap around python code to communicate results to a Healthchecks check."""

    def __init__(
        self,
        client: Union[Client, AsyncClient],
        uuid: str = "",
        slug: str = "",
        suppress_exceptions: bool = False,
    ) -> None:
        """A context manager to wrap around python code to communicate results to a Healthchecks check.

        Args:
            client (Union[Client, AsyncClient]): healthchecks_io client, async or sync
            uuid (str): uuid of the check. Defaults to "".
            slug (str): slug of the check, exclusion wiht uuid. Defaults to "".
            suppress_exceptions (bool): If true, do not raise any exceptions. Defaults to False.

        Raises:
            Exception: Raised if a slug and a uuid is passed
        """
        if uuid == "" and slug == "":
            raise Exception("Must pass a slug or an uuid")
        self.client: Union[Client, AsyncClient] = client
        self.uuid: str = uuid
        self.slug: str = slug
        self.log_lines: List[str] = list()
        self.suppress_exceptions: bool = suppress_exceptions

    def add_log(self, line: str) -> None:
        """Add a line to the context manager's log that is sent with the check.

        Args:
            line (str): String to add to the logs
        """
        self.log_lines.append(line)

    def __enter__(self) -> "CheckTrap":
        """Enter the context manager.

        Sends a start ping to the check represented by self.uuid or self.slug.

        Raises:
            WrongClientError: Raised when using an AsyncClient with this as a sync client manager
            PingFailedError: When a ping fails for any reason not handled by a custom exception
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404 or response text has "not found" in it
            BadAPIRequestError: Raised when status_code is 400, or if you pass a uuid and a slug, or if
                pinging by a slug and do not have a ping key set
            HCAPIRateLimitError: Raised when status code is 429 or response text has "rate limited" in it
            NonUniqueSlugError: Raused when status code is 409.

        Returns:
            CheckTrap: self
        """
        if isinstance(self.client, AsyncClient):
            raise WrongClientError("You passed an AsyncClient, use this as an async context manager")
        result = self.client.start_ping(uuid=self.uuid, slug=self.slug)
        if not result[0]:
            raise PingFailedError(result[1])
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit the context manager.

        If there is an exception, add it to any log lines and send a fail ping.
        Otherwise, send a success ping with any log lines appended.

        Args:
            exc_type (Optional[Type[BaseException]]): [description]
            exc (Optional[BaseException]): [description]
            traceback (Optional[TracebackType]): [description]

        Returns:
            Optional[bool]: self.suppress_exceptions, if true will not raise any exceptions
        """
        if exc_type is None:
            self.client.success_ping(self.uuid, self.slug, data="\n".join(self.log_lines))
        else:
            self.add_log(str(exc))
            self.add_log(str(traceback))
            self.client.fail_ping(self.uuid, self.slug, data="\n".join(self.log_lines))
        return self.suppress_exceptions

    async def __aenter__(self) -> "CheckTrap":
        """Enter the context manager.

        Sends a start ping to the check represented by self.uuid or self.slug.

        Raises:
            WrongClientError: Raised when using an AsyncClient with this as a sync client manager
            PingFailedError: When a ping fails for any reason not handled by a custom exception
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404 or response text has "not found" in it
            BadAPIRequestError: Raised when status_code is 400, or if you pass a uuid and a slug, or if
                pinging by a slug and do not have a ping key set
            HCAPIRateLimitError: Raised when status code is 429 or response text has "rate limited" in it
            NonUniqueSlugError: Raused when status code is 409.

        Returns:
            CheckTrap: self
        """
        if isinstance(self.client, Client):
            raise WrongClientError("You passed a sync Client, use this as a regular context manager")
        result = await self.client.start_ping(self.uuid, self.slug)
        if not result[0]:
            raise PingFailedError(result[1])
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit the context manager.

        If there is an exception, add it to any log lines and send a fail ping.
        Otherwise, send a success ping with any log lines appended.

        Args:
            exc_type (Optional[Type[BaseException]]): [description]
            exc (Optional[BaseException]): [description]
            traceback (Optional[TracebackType]): [description]

        Returns:
            Optional[bool]: self.suppress_exceptions, if true will not raise any exceptions
        """
        if exc_type is None:
            # ignore typing, if we've gotten here we know its an async client
            await self.client.success_ping(  # type: ignore
                self.uuid, self.slug, data="\n".join(self.log_lines)
            )
        else:
            self.add_log(str(exc))
            self.add_log(str(traceback))
            await self.client.fail_ping(  # type: ignore
                self.uuid, self.slug, data="\n".join(self.log_lines)
            )
        return self.suppress_exceptions
