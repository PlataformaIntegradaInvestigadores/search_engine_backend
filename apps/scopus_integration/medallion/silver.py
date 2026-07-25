from typing import Any, Dict, Iterable, List, Tuple

from apps.scopus_integration.medallion.repository import ScopusMedallionRepository
from apps.scopus_integration.medallion.schemas import SilverAffiliation, SilverArticle, SilverAuthor


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _first(*values: Any) -> str:
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


class SilverTransformer:
    def __init__(self, repository: ScopusMedallionRepository) -> None:
        self.repository = repository

    def transform(self) -> Dict[str, int]:
        articles: List[Dict[str, Any]] = []
        authors: Dict[str, Dict[str, Any]] = {}
        affiliations: Dict[str, Dict[str, Any]] = {}

        for raw_article in self.repository.iter_raw_articles():
            silver_article, article_authors, article_affiliations = self.transform_article(raw_article)
            if silver_article:
                articles.append(silver_article.model_dump())
            for author in article_authors:
                authors[author.author_id] = author.model_dump()
            for affiliation in article_affiliations:
                affiliations[affiliation.affiliation_id] = affiliation.model_dump()

        return {
            "articles": self.repository.upsert_silver_articles(articles),
            "authors": self.repository.upsert_silver_authors(authors.values()),
            "affiliations": self.repository.upsert_silver_affiliations(affiliations.values()),
        }

    def transform_article(self, raw_article: Dict[str, Any]) -> Tuple[SilverArticle, List[SilverAuthor], List[SilverAffiliation]]:
        scopus_id = _first(raw_article.get("dc:identifier"), raw_article.get("eid"))
        title = _first(raw_article.get("dc:title"), raw_article.get("title"))
        abstract = _first(raw_article.get("dc:description"), raw_article.get("description"), raw_article.get("abstract"))
        cover_date = _first(raw_article.get("prism:coverDate"), raw_article.get("coverDate"))
        publication_year = cover_date[:4] if cover_date else raw_article.get("year")
        author_entries = _as_list(raw_article.get("author"))
        affiliation_entries = _as_list(raw_article.get("affiliation"))

        authors = [self._author_from_entry(entry) for entry in author_entries if isinstance(entry, dict)]
        affiliations = [self._affiliation_from_entry(entry) for entry in affiliation_entries if isinstance(entry, dict)]
        author_ids = list(dict.fromkeys(author.author_id for author in authors if author.author_id))
        affiliation_ids = list(dict.fromkeys(affiliation.affiliation_id for affiliation in affiliations if affiliation.affiliation_id))
        countries = list(dict.fromkeys(affiliation.country for affiliation in affiliations if affiliation.country))

        topics = [
            item
            for item in _as_list(raw_article.get("authkeywords") or raw_article.get("idxterms"))
            if isinstance(item, str)
        ]

        article = SilverArticle(
            scopus_id=scopus_id,
            title=title,
            abstract=abstract,
            cover_date=cover_date,
            publication_year=publication_year,
            doi=_first(raw_article.get("prism:doi"), raw_article.get("doi")),
            cited_by_count=int(raw_article.get("citedby-count") or 0),
            subtype=_first(raw_article.get("subtype"), raw_article.get("subtypeDescription")),
            author_ids=author_ids,
            affiliation_ids=affiliation_ids,
            countries=countries,
            topics=topics,
            raw_metadata=raw_article.get("_metadata", {}),
        )
        return article, authors, affiliations

    @staticmethod
    def _author_from_entry(entry: Dict[str, Any]) -> SilverAuthor:
        affiliation_ids = [
            str(item.get("@id") or item.get("id") or item.get("afid"))
            for item in _as_list(entry.get("affiliation"))
            if isinstance(item, dict) and (item.get("@id") or item.get("id") or item.get("afid"))
        ]
        return SilverAuthor(
            author_id=_first(entry.get("authid"), entry.get("@auid"), entry.get("author_id")),
            indexed_name=_first(entry.get("authname"), entry.get("indexed-name"), entry.get("ce:indexed-name")),
            surname=_first(entry.get("surname"), entry.get("ce:surname")),
            given_name=_first(entry.get("given-name"), entry.get("ce:given-name")),
            initials=_first(entry.get("initials"), entry.get("ce:initials")),
            affiliation_ids=affiliation_ids,
        )

    @staticmethod
    def _affiliation_from_entry(entry: Dict[str, Any]) -> SilverAffiliation:
        return SilverAffiliation(
            affiliation_id=_first(entry.get("afid"), entry.get("@id"), entry.get("id")),
            name=_first(entry.get("affilname"), entry.get("name")),
            city=_first(entry.get("affiliation-city"), entry.get("city")),
            country=_first(entry.get("affiliation-country"), entry.get("country")),
        )
