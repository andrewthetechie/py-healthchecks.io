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

from healthchecks_io.schemas import checks


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
    def _finalizer_method(self):
        """Finalizer method is called by weakref.finalize when the object is dereferenced to do cleanup of clients."""
        pass

    @abstractmethod
    def get_checks(self, tags: Optional[List[str]]) -> List[checks.Check]:
        """Calls the API's /checks/ endpoint to get a list of checks."""
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
