from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from urllib.parse import parse_qsl
from urllib.parse import ParseResult
from urllib.parse import unquote
from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.parse import urlparse
from weakref import finalize

from httpx import Response

from .exceptions import BadAPIRequestError
from .exceptions import CheckNotFoundError
from .exceptions import HCAPIAuthError
from .exceptions import HCAPIError
from .exceptions import HCAPIRateLimitError
from .exceptions import NonUniqueSlugError


class AbstractClient(ABC):
    """An abstract client class that can be implemented by client classes."""

    def __init__(
        self,
        api_key: str = "",
        ping_key: str = "",
        api_url: str = "https://healthchecks.io/api/",
        ping_url: str = "https://hc-ping.com/",
        api_version: int = 1,
    ) -> None:
        """An AbstractClient that other clients can implement.

        Args:
            api_key (str): Healthchecks.io API key. Defaults to an empty string.
            ping_key (str): Healthchecks.io Ping key. Defaults to an empty string.
            api_url (str): API URL. Defaults to "https://healthchecks.io/api/".
            ping_url (str): Ping API url. Defaults to "https://hc-ping.com/".
            api_version (int): Versiopn of the api to use. Defaults to 1.
        """
        self._api_key = api_key
        self._ping_key = ping_key
        if not api_url.endswith("/"):
            api_url = f"{api_url}/"
        if not ping_url.endswith("/"):
            ping_url = f"{ping_url}/"
        self._api_url = urljoin(api_url, f"v{api_version}/")
        self._ping_url = ping_url
        self._finalizer = finalize(self, self._finalizer_method)

    @abstractmethod
    def _finalizer_method(self) -> None:  # pragma: no cover
        """Finalizer method is called by weakref.finalize when the object is dereferenced to do cleanup of clients."""
        pass

    def _get_api_request_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Get a full request url for the healthchecks api.

        Args:
            path (str): Path to request from
            params (Optional[Dict[str, str]], optional): URL Parameters. Defaults to None.

        Returns:
            str: url
        """
        url = urljoin(self._api_url, path)
        return self._add_url_params(url, params) if params is not None else url

    def _get_ping_url(self, uuid: str, slug: str, endpoint: str) -> str:
        """Get a url for sending a ping.

        Can take either a UUID or a Slug, but not both.

        Args:
            uuid (str): uuid of a check
            slug (str): slug of a check
            endpoint (str): Endpoint to request

        Raises:
            BadAPIRequestError: Raised if you pass a uuid and a slug, or if pinging by a slug and do not have a
            ping key set

        Returns:
            str: url for this
        """
        if uuid == "" and slug == "" or uuid != "" and slug != "":
            raise BadAPIRequestError("Must pass a uuid or a slug")

        if slug != "" and self._ping_key == "":
            raise BadAPIRequestError("If pinging by slug, must have a ping key set")

        if uuid != "":
            return self._get_ping_url_uuid(uuid, endpoint)
        return self._get_ping_url_slug(slug, endpoint)

    def _get_ping_url_uuid(self, uuid: str, endpoint: str) -> str:
        """Get a ping url for a check with a uuid.

        Args:
            uuid (str): uuid of a check
            endpoint (str): Endpoint to request

        Returns:
            str: ping url
        """
        return urljoin(self._ping_url, f"{uuid}{endpoint}")

    def _get_ping_url_slug(self, slug: str, endpoint: str) -> str:
        """Get a ping url for a check with a slug.

        Args:
            slug (str): slug of a check
            endpoint (str): Endpoint to request

        Returns:
            str: ping url
        """
        return urljoin(self._ping_url, f"{self._ping_key}/{slug}{endpoint}")

    @property
    def is_closed(self) -> bool:
        """Is the client closed?

        Returns:
            bool: is the client closed
        """
        return self._client.is_closed  # type: ignore

    @staticmethod
    def check_response(response: Response) -> Response:
        """Checks a healthchecks.io response.

        Args:
            response (Response): a response from the healthchecks.io api

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404
            BadAPIRequestError: Raised when status_code is 400
            HCAPIRateLimitError: Raised when status code is 429

        Returns:
            Response: the passed in response object
        """
        if response.status_code == 401 or response.status_code == 403:
            raise HCAPIAuthError("Auth failure when getting checks")

        if str(response.status_code).startswith("5"):
            raise HCAPIError(
                f"Error when reaching out to HC API at {response.request.url}. "
                f"Status Code {response.status_code}. Response {response.text}"
            )

        if response.status_code == 429:
            raise HCAPIRateLimitError(f"Rate limited on {response.request.url}")

        if response.status_code == 404:
            raise CheckNotFoundError(f"CHeck not found at {response.request.url}")

        if response.status_code == 400:
            raise BadAPIRequestError(f"Bad request when requesting {response.request.url}. {response.text}")

        return response

    @staticmethod
    def check_ping_response(response: Response) -> Response:
        """Checks a healthchecks.io ping response.

        Args:
            response (Response): a response from the healthchecks.io api

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx
            CheckNotFoundError: Raised when status_code is 404 or response text has "not found" in it
            BadAPIRequestError: Raised when status_code is 400
            HCAPIRateLimitError: Raised when status code is 429 or response text has "rate limited" in it
            NonUniqueSlugError: Raused when status code is 409.

        Returns:
            Response: the passed in response object
        """
        if response.status_code == 401 or response.status_code == 403:
            raise HCAPIAuthError("Auth failure when pinging")

        if str(response.status_code).startswith("5"):
            raise HCAPIError(
                f"Error when reaching out to HC API at {response.request.url}. "
                f"Status Code {response.status_code}. Response {response.text}"
            )

        # ping api docs say it can return a 200 with not found for a not found check.
        # in my testing, its always a 404, but this will cover what the docs say
        # https://healthchecks.io/docs/http_api/
        if response.status_code == 404 or "not found" in response.text:
            raise CheckNotFoundError(f"CHeck not found at {response.request.url}")

        if "rate limited" in response.text or response.status_code == 429:
            raise HCAPIRateLimitError(f"Rate limited on {response.request.url}")

        if response.status_code == 400:
            raise BadAPIRequestError(f"Bad request when requesting {response.request.url}. {response.text}")

        if response.status_code == 409:
            raise NonUniqueSlugError(f"Bad request, slug conflict {response.request.url}. {response.text}")

        return response

    @staticmethod
    def _add_url_params(url: str, params: Dict[str, Union[str, int, bool]], replace: bool = True) -> str:
        """Add GET params to provided URL being aware of existing.

        :param url: string of target URL
        :param params: dict containing requested params to be added
        :param replace: bool True If true, replace params if they exist with new values, otherwise append
        :return: string with updated URL

        >> url = 'http://stackoverflow.com/test?answers=true'
        >> new_params = {'answers': False, 'data': ['some','values']}
        >> add_url_params(url, new_params)
        'http://stackoverflow.com/test?data=some&data=values&answers=false'
        """
        # Unquoting URL first so we don't loose existing args
        url = unquote(url)
        # Extracting url info
        parsed_url = urlparse(url)
        # Extracting URL arguments from parsed URL
        get_args = parsed_url.query
        # Converting URL arguments to dict
        parsed_get_args = dict(parse_qsl(get_args))

        # we want all string values
        parsed_params = {k: str(val) for k, val in params.items()}

        if replace:
            # Merging URL arguments dict with new params
            parsed_get_args.update(parsed_params)
            extra_parameters = ""
        else:
            # get all the duplicated keys from params and urlencode them, we'll concat this to the params string later
            duplicated_params = [x for x in params if x in parsed_get_args]
            # get all the args that aren't duplicated and add them to parsed_get_args
            parsed_get_args.update({key: parsed_params[key] for key in [x for x in params if x not in parsed_get_args]})
            # if we have any duplicated parameters, urlencode them, we append them later
            extra_parameters = (
                f"&{urlencode({key: params[key] for key in duplicated_params}, doseq=True)}"
                if len(duplicated_params) > 0
                else ""
            )

        # Converting URL argument to proper query string
        encoded_get_args = f"{urlencode(parsed_get_args, doseq=True)}{extra_parameters}"
        # Creating new parsed result object based on provided with new
        # URL arguments. Same thing happens inside of urlparse.
        new_url = ParseResult(
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            encoded_get_args,
            parsed_url.fragment,
        ).geturl()

        return new_url
