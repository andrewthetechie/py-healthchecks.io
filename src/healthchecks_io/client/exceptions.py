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
