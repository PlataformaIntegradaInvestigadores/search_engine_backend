from typing import Any, Callable, Dict, Iterable

from neomodel import db


class Neo4jGraphPublisher:
    def __init__(self, query_executor: Callable | None = None, batch_size: int = 1000) -> None:
        self.query_executor = query_executor or db.cypher_query
        self.batch_size = batch_size

    def publish(self, graph_entities: Iterable[Dict[str, Any]]) -> Dict[str, int]:
        authors: Dict[str, Dict[str, Any]] = {}

        for entity in graph_entities:
            affiliations = {
                str(item.get("affiliation_id")): item.get("name", "")
                for item in entity.get("affiliations", [])
                if item.get("affiliation_id")
            }
            for item in entity.get("authors", []):
                author_id = str(item.get("author_id") or "").strip()
                if not author_id:
                    continue
                affiliation_ids = [str(value) for value in item.get("affiliation_ids", [])]
                current_affiliation = next(
                    (affiliations[value] for value in affiliation_ids if affiliations.get(value)),
                    "",
                )
                authors[author_id] = {
                    "scopus_id": author_id,
                    "first_name": item.get("given_name", ""),
                    "last_name": item.get("surname", ""),
                    "auth_name": item.get("indexed_name", ""),
                    "initials": item.get("initials", ""),
                    "citation_count": int(item.get("citation_count") or 0),
                    "current_affiliation": current_affiliation,
                }

        query = """
            UNWIND $authors AS item
            MATCH (author:Author {authid: item.scopus_id})
            SET author.given_name = CASE
                    WHEN item.first_name <> '' THEN item.first_name
                    ELSE coalesce(author.given_name, '')
                END,
                author.surname = CASE
                    WHEN item.last_name <> '' THEN item.last_name
                    ELSE coalesce(author.surname, '')
                END,
                author.authname = CASE
                    WHEN item.auth_name <> '' THEN item.auth_name
                    ELSE coalesce(author.authname, '')
                END,
                author.initials = CASE
                    WHEN item.initials <> '' THEN item.initials
                    ELSE coalesce(author.initials, '')
                END,
                author.citation_count = CASE
                    WHEN item.citation_count > 0 THEN item.citation_count
                    ELSE coalesce(author.citation_count, 0)
                END,
                author.current_affiliation = CASE
                    WHEN item.current_affiliation <> '' THEN item.current_affiliation
                    ELSE coalesce(author.current_affiliation, '')
                END,
                author.updated = true
            RETURN count(author)
        """

        updated = 0
        author_values = list(authors.values())
        for offset in range(0, len(author_values), self.batch_size):
            batch = author_values[offset:offset + self.batch_size]
            results, _ = self.query_executor(query, {"authors": batch})
            updated += int(results[0][0]) if results else 0

        return {"authors": updated}
