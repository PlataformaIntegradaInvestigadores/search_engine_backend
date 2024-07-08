from abc import ABC, abstractmethod
from typing import List


class AuthorRepository(ABC):
    @abstractmethod
    def find_by_id(self, scopus_id) -> object:
        pass

    @abstractmethod
    def find_all(self, page_size=None, page=None) -> (List[object], int):
        pass

    @abstractmethod
    def save(self, author: object) -> object:
        pass

    @abstractmethod
    def update(self, author: object) -> object:
        pass

    @abstractmethod
    def bulk_create(self, authors: List[object]) -> List[object]:
        pass

    @abstractmethod
    def find_authors_by_query(self, name: str, page_size=None, page=None) -> List[object]:
        pass

    @abstractmethod
    def find_authors_by_affiliation_filter(self, filter_type: str, affiliations_ids: List[str],
                                           authors_ids: List[str]) -> List[object]:
        pass

    @abstractmethod
    def find_community(self, authors_ids: List[str]):
        pass

    @abstractmethod
    def find_most_relevant_authors_by_topic(self, topic: str, authors_number: int):
        pass

    @abstractmethod
    def authors_count(self) -> int:
        pass
