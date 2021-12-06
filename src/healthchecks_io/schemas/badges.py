"""
Schemas for badges
https://healthchecks.io/docs/api/
"""
from pydantic import BaseModel, AnyUrl
from typing import Dict


class Badges(BaseModel):
    svg: str
    svg3: str
    json_url: str
    json3_url: str
    shields: str
    shields3: str

    @classmethod
    def from_api_result(cls, badges_dict: Dict[str, str]) -> 'Badges':
        """
        Converts an API response into a Badges object
        """
        badges_dict['json_url'] = badges_dict['json']
        badges_dict['json3_url'] = badges_dict['json3']
        return cls(**badges_dict)