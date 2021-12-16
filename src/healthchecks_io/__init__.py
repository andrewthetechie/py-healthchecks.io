"""Py Healthchecks.Io."""
VERSION = "0.1"  # noqa: E402

from .client import AsyncClient  # noqa: F401, E402
from .client import Client  # noqa: F401, E402
from .client.exceptions import BadAPIRequestError  # noqa: F401, E402
from .client.exceptions import CheckNotFoundError  # noqa: F401, E402
from .client.exceptions import HCAPIAuthError  # noqa: F401, E402
from .client.exceptions import HCAPIError  # noqa: F401, E402
from .client.exceptions import HCAPIRateLimitError  # noqa: F401, E402
from .client.exceptions import NonUniqueSlugError  # noqa: F401, E402
from .schemas import Check, CheckCreate, CheckPings, CheckStatuses  # noqa: F401, E402
from .schemas import Integration, Badges, CheckUpdate  # noqa: F401, E402

__all__ = [
    "AsyncClient",
    "Client",
    "BadAPIRequestError",
    "CheckNotFoundError",
    "HCAPIAuthError",
    "HCAPIError",
    "CheckNotFoundError",
    "HCAPIRateLimitError",
    "NonUniqueSlugError",
    "Check",
    "CheckCreate",
    "CheckUpdate",
    "CheckPings",
    "CheckStatuses",
    "Integration",
    "Badges",
]
