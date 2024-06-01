"""Py Healthchecks.Io."""

# set by poetry-dynamic-versioning
__version__ = "0.4.3"  # noqa: E402

from .client import AsyncClient  # noqa: F401, E402
from .client import Client  # noqa: F401, E402
from .client import CheckTrap  # noqa: F401, E402
from .client.exceptions import BadAPIRequestError  # noqa: F401, E402
from .client.exceptions import CheckNotFoundError  # noqa: F401, E402
from .client.exceptions import HCAPIAuthError  # noqa: F401, E402
from .client.exceptions import HCAPIError  # noqa: F401, E402
from .client.exceptions import HCAPIRateLimitError  # noqa: F401, E402
from .client.exceptions import NonUniqueSlugError  # noqa: F401, E402
from .client.exceptions import WrongClientError  # noqa: F401, E402
from .client.exceptions import PingFailedError  # noqa: F401, E402
from .schemas import Check, CheckCreate, CheckPings, CheckStatuses  # noqa: F401, E402
from .schemas import Integration, Badges, CheckUpdate  # noqa: F401, E402

__all__ = [
    "AsyncClient",
    "Client",
    "CheckTrap",
    "BadAPIRequestError",
    "CheckNotFoundError",
    "HCAPIAuthError",
    "HCAPIError",
    "CheckNotFoundError",
    "HCAPIRateLimitError",
    "NonUniqueSlugError",
    "WrongClientError",
    "PingFailedError",
    "Check",
    "CheckCreate",
    "CheckUpdate",
    "CheckPings",
    "CheckStatuses",
    "Integration",
    "Badges",
    "__version__",
]
