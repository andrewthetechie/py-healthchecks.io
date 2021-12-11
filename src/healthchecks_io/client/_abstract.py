from abc import ABC
from abc import abstractmethod
from json import dumps
from typing import Dict
from typing import List
from typing import Optional
from urllib.parse import parse_qsl
from urllib.parse import ParseResult
from urllib.parse import unquote
from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.parse import urlparse
from weakref import finalize

from httpx import Client
from httpx import Response

from .exceptions import BadAPIRequestError
from .exceptions import CheckNotFoundError
from .exceptions import HCAPIAuthError
from .exceptions import HCAPIError
from healthchecks_io.schemas import badges
from healthchecks_io.schemas import checks
from healthchecks_io.schemas import integrations


class AbstractClient(ABC):
    """An abstract client class that can be implemented by client classes."""

    def __init__(
        self,
        api_key: str,
        api_url: Optional[str] = "https://healthchecks.io/api/",
        api_version: Optional[int] = 1,
        client: Optional[Client] = None,
    ) -> None:
        """An AbstractClient that other clients can implement.

        Args:
            api_key (str): Healthchecks.io API key
            api_url (Optional[str], optional): API URL. Defaults to "https://healthchecks.io/api/".
            api_version (Optional[int], optional): Versiopn of the api to use. Defaults to 1.
            client (Optional[Client], optional): A httpx.Client. If not
                passed in, one will be created for this object. Defaults to None.
        """
        self._api_key = api_key
        self._client = client
        if not api_url.endswith("/"):
            api_url = f"{api_url}/"
        self._api_url = urljoin(api_url, f"v{api_version}/")
        self._finalizer = finalize(self, self._finalizer_method)

    @abstractmethod
    def _finalizer_method(self):  # pragma: no cover
        """Finalizer method is called by weakref.finalize when the object is dereferenced to do cleanup of clients."""
        pass

    @abstractmethod
    def get_checks(
        self, tags: Optional[List[str]]
    ) -> List[checks.Check]:  # pragma: no cover
        """Calls the API's /checks/ endpoint to get a list of checks."""
        pass

    @abstractmethod
    def get_check(self, check_id: str) -> checks.Check:  # pragma: no cover
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
        pass

    @abstractmethod
    def pause_check(self, check_id: str) -> checks.Check:  # pragma: no cover
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
        pass

    @abstractmethod
    def delete_check(self, check_id: str) -> checks.Check:  # pragma: no cover
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
        pass

    @abstractmethod
    def get_check_pings(
        self, check_id: str
    ) -> List[checks.CheckPings]:  # pragma: no cover
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
        pass

    @abstractmethod
    def get_check_flips(
        self,
        check_id: str,
        seconds: Optional[int] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> List[checks.CheckStatuses]:  # pragma: no cover
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
        pass

    @abstractmethod
    def get_integrations(
        self,
    ) -> List[Optional[integrations.Integration]]:  # pragma: no cover
        """Returns a list of integrations belonging to the project.

        Raises:
            HCAPIAuthError: Raised when status_code == 401 or 403
            HCAPIError: Raised when status_code is 5xx

        Returns:
            List[Optional[integrations.Integration]]: List of integrations for the project

        """
        pass

    @abstractmethod
    def get_badges(self) -> Dict[str, badges.Badges]:  # pragma: no cover
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
        pass

    def _get_api_request_url(
        self, path: str, params: Optional[Dict[str, str]] = None
    ) -> str:
        """Get a full request url for the healthchecks api.

        Args:
            path (str): Path to request from
            params (Optional[Dict[str, str]], optional): URL Parameters. Defaults to None.

        Returns:
            str: url
        """
        url = urljoin(self._api_url, path)
        return self._add_url_params(url, params) if params is not None else url

    @property
    def is_closed(self) -> bool:
        """Is the client closed?

        Returns:
            bool: is the client closed
        """
        return self._client.is_closed

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

        if response.status_code == 404:
            raise CheckNotFoundError(f"CHeck not found at {response.request.url}")

        if response.status_code == 400:
            raise BadAPIRequestError(
                f"Bad request when requesting {response.request.url}. {response.text}"
            )

        return response

    @staticmethod
    def _add_url_params(url: str, params: Dict[str, str], replace: bool = True):
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
        if replace:
            # Merging URL arguments dict with new params
            parsed_get_args.update(params)
            extra_parameters = ""
        else:
            # get all the duplicated keys from params and urlencode them, we'll concat this to the params string later
            duplicated_params = [x for x in params if x in parsed_get_args]
            # get all the args that aren't duplicated and add them to parsed_get_args
            parsed_get_args.update(
                {
                    key: params[key]
                    for key in [x for x in params if x not in parsed_get_args]
                }
            )
            # if we have any duplicated parameters, urlencode them, we append them later
            extra_parameters = (
                f"&{urlencode({key: params[key] for key in duplicated_params}, doseq=True)}"
                if len(duplicated_params) > 0
                else ""
            )

        # Bool and Dict values should be converted to json-friendly values
        # you may throw this part away if you don't like it :)
        parsed_get_args.update(
            {
                k: dumps(v)
                for k, v in parsed_get_args.items()
                if isinstance(v, (bool, dict))
            }
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
