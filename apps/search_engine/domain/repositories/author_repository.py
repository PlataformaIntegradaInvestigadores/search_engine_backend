from abc import ABC, abstractmethod
from typing import List


class AuthorRepository(ABC):
    @abstractmethod
    def find_by_id(self, scopus_id) -> object:
        pass

    @abstractmethod
    def get_all(self, page_size=None, page=None) -> List[object]:
        pass

    @abstractmethod
    def save(self, author: object) -> object:
        pass

    @abstractmethod
    def update(self, author: object) -> object:
        pass

    def bulk_create(self, authors: List[object]) -> List[object]:
        pass
