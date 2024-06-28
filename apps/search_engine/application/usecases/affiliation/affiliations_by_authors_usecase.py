from typing import List

from apps.search_engine.domain.entities.affiliation import Affiliation
from apps.search_engine.domain.repositories.affiliation_repository import AffiliationRepository


class AffiliationByAuthorsUsecase:
    def __init__(self, repository: AffiliationRepository):
        self.repository = repository

    def execute(self, authors: List[str]) -> List[object]:
        return self.repository.find_affiliations_by_authors(authors)
