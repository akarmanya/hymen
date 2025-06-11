from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class SpiderDomain(str, Enum):
    FINOS = "finos"


class RiskItem(BaseModel):
    risk_id: str
    title: str
    content: str
    url: str


class RiskSection(BaseModel):
    category: str
    risks: List[RiskItem]


class MitigationItem(BaseModel):
    mitigation_id: str
    title: str
    content: str
    url: str


class MitigationSection(BaseModel):
    category: str
    mitigations: List[MitigationItem]


class FINOSCatalogue(BaseModel):
    domain: SpiderDomain = SpiderDomain.FINOS
    risk_sections: List[RiskSection]
    mitigation_sections: List[MitigationSection]
