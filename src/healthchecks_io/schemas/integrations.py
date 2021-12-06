"""
Schemas for integrations
https://healthchecks.io/docs/api/
"""
from typing import Dict

from pydantic import BaseModel


class Integration(BaseModel):
    id: str
    name: str
    kind: str

    @classmethod
    def from_api_result(cls, integration_dict: Dict[str, str]) -> "Integration":
        return cls(**integration_dict)
