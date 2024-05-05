"""Schemas for badges.

https://healthchecks.io/docs/api/
"""

from typing import Dict

from pydantic import BaseModel


class Badges(BaseModel):
    """Object with the Badges urls."""

    svg: str
    svg3: str
    json_url: str
    json3_url: str
    shields: str
    shields3: str

    @classmethod
    def from_api_result(cls, badges_dict: Dict[str, str]) -> "Badges":
        """Converts a dictionary from the healthchecks api into a Badges object."""
        badges_dict["json_url"] = badges_dict["json"]
        badges_dict["json3_url"] = badges_dict["json3"]
        return cls(**badges_dict)
