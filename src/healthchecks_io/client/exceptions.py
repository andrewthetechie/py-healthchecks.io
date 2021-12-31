"""healthchecks_io exceptions."""


class HCAPIError(Exception):
    """API Exception for when we have an error with the healthchecks api."""

    ...


class HCAPIAuthError(HCAPIError):
    """Thrown when we fail to auth to the Healthchecks api."""

    ...


class CheckNotFoundError(HCAPIError):
    """Thrown when getting a check returns a 404."""

    ...


class BadAPIRequestError(HCAPIError):
    """Thrown when an api request returns a 400."""

    ...


class HCAPIRateLimitError(HCAPIError):
    """Thrown when the api returns a rate limit response."""

    ...


class NonUniqueSlugError(HCAPIError):
    """Thrown when the api returns a 409 when pinging."""

    ...


class WrongClientError(HCAPIError):
    """Thrown when trying to use a CheckTrap with the wrong client type."""

    ...


class PingFailedError(HCAPIError):
    """Thrown when a ping fails."""

    ...
