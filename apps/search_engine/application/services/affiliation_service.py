from typing import List

from neomodel import db

from apps.search_engine.domain.entities.affiliation import Affiliation
from apps.search_engine.domain.repositories.affiliation_repository import AffiliationRepository


class AffiliationService(AffiliationRepository):
    def get_total_affiliations(self) -> int:
        try:
            query = "MATCH (a:Affiliation) RETURN count(a) AS total"
            results, meta = db.cypher_query(query)
            total_affiliations = results[0][0]
            return total_affiliations
        except Exception as e:
            raise ValueError(f"Error finding total affiliations: {e}")

    def find_by_id(self, scopus_id) -> object:
        try:
            affiliation = Affiliation.nodes.get_or_none(scopus_id=scopus_id)
            return affiliation
        except Exception as e:
            raise ValueError(f"Error finding affiliation: {e}")

    def find_by_name(self, affiliation_name: str) -> List[object]:
        pass

    def save(self, affiliation: object) -> object:
        pass

    def update(self, affiliation: object) -> object:
        pass

    def bulk_create(self, affiliations: List[dict]) -> List[object]:
        try:
            return Affiliation.get_or_create(*affiliations)
        except Exception as e:
            raise ValueError(f"Error creating affiliations: {e}")

    def find_all(self, page_number: int = None, page_size: int = 10) -> List[object]:
        try:
            skip = (page_number - 1) * page_size
            query = f"MATCH (a:Affiliation) RETURN a SKIP {skip} LIMIT {page_size}"
            results, meta = db.cypher_query(query)
            affiliations = [Affiliation.inflate(row[0]) for row in results]
            return affiliations
        except Exception as e:
            raise ValueError(f"Error finding affiliations: {e}")
