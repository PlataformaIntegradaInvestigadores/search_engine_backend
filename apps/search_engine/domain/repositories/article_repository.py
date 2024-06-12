from abc import ABC, abstractmethod
from typing import List


class ArticleRepository(ABC):
    @abstractmethod
    def find_by_id(self, article_id) -> object:
        pass

    @abstractmethod
    def save(self, article) -> object:
        pass

    @abstractmethod
    def update(self, article) -> object:
        pass

    @abstractmethod
    def get_all(self, page_number=None, page_size=None) -> List[object]:
        pass

    @abstractmethod
    def get_total_articles(self) -> int:
        pass

    @abstractmethod
    def bulk_create(self, articles: List[dict]) -> List[object]:
        pass
