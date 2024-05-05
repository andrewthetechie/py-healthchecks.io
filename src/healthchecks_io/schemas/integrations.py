"""Schemas for integrations.

https://healthchecks.io/docs/api/
"""

from pydantic import BaseModel


class Integration(BaseModel):
    """Schema for an integration object."""

    id: str
    name: str
    kind: str

    @classmethod
    def from_api_result(cls, integration_dict: dict[str, str]) -> "Integration":
        """Converts a dictionary from the healthchecks api into an Integration object."""
        return cls(**integration_dict)
