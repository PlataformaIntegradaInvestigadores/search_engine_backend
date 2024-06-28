from abc import ABC, abstractmethod
from typing import List


class AffiliationRepository(ABC):
    @abstractmethod
    def find_by_id(self, scopus_id) -> object:
        pass

    @abstractmethod
    def find_by_name(self, affiliation_name: str) -> List[object]:
        pass

    @abstractmethod
    def save(self, affiliation: object) -> object:
        pass

    @abstractmethod
    def update(self, affiliation: object) -> object:
        pass

    @abstractmethod
    def bulk_create(self, affiliations: List[dict]) -> List[object]:
        pass

    @abstractmethod
    def find_all(self, page_number: int = 1, page_size: int = 10) -> List[object]:
        pass

    @abstractmethod
    def find_total_affiliations(self) -> int:
        pass

    @abstractmethod
    def find_affiliations_by_authors(self, authors: List[str]) -> List[object]:
        pass
