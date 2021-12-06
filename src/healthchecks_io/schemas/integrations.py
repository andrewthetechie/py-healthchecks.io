"""
Schemas for integrations
https://healthchecks.io/docs/api/
"""
from pydantic import BaseModel


class Integration(BaseModel):
    id: str
    name: str
    kind: str
