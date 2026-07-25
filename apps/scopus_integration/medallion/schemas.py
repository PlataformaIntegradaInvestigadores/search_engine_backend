from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SilverAuthor(BaseModel):
    author_id: str
    indexed_name: str = ""
    surname: str = ""
    given_name: str = ""
    initials: str = ""
    affiliation_ids: List[str] = Field(default_factory=list)
    document_count: int = 0
    citation_count: int = 0
    h_index: int = 0
    source: str = "scopus"


class SilverAffiliation(BaseModel):
    affiliation_id: str
    name: str = ""
    city: str = ""
    country: str = ""
    document_count: int = 0
    source: str = "scopus"

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return (value or "").strip()


class SilverArticle(BaseModel):
    scopus_id: str
    title: str = ""
    abstract: str = ""
    cover_date: Optional[str] = None
    publication_year: Optional[int] = None
    doi: str = ""
    cited_by_count: int = 0
    subtype: str = ""
    author_ids: List[str] = Field(default_factory=list)
    affiliation_ids: List[str] = Field(default_factory=list)
    countries: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    source: str = "scopus"
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("scopus_id")
    @classmethod
    def normalize_scopus_id(cls, value: str) -> str:
        return (value or "").replace("SCOPUS_ID:", "").strip()

    @field_validator("publication_year", mode="before")
    @classmethod
    def parse_publication_year(cls, value: Any) -> Optional[int]:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value[:4].isdigit():
            return int(value[:4])
        return None

    @field_validator("cover_date")
    @classmethod
    def validate_cover_date(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        try:
            datetime.fromisoformat(value[:10])
            return value[:10]
        except ValueError:
            return None


class GoldMlFeature(BaseModel):
    doc_id: str
    doc_type: str
    title: str = ""
    abstract: str = ""
    topics: List[str] = Field(default_factory=list)
    authors: List[Dict[str, Any]] = Field(default_factory=list)
    affiliations: List[Dict[str, Any]] = Field(default_factory=list)
    text: str
    source: str = "scopus"


class GoldGraphEntity(BaseModel):
    article: Dict[str, Any]
    authors: List[Dict[str, Any]] = Field(default_factory=list)
    affiliations: List[Dict[str, Any]] = Field(default_factory=list)
    topics: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    source: str = "scopus"


class GoldDashboardMetrics(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    totals: Dict[str, int] = Field(default_factory=dict)
    by_year: List[Dict[str, Any]] = Field(default_factory=list)
    by_country: List[Dict[str, Any]] = Field(default_factory=list)
    by_affiliation: List[Dict[str, Any]] = Field(default_factory=list)
    by_topic: List[Dict[str, Any]] = Field(default_factory=list)
    source: str = "scopus"
