from abc import ABC, abstractmethod
from typing import List, Tuple


class ArticleRepository(ABC):
    @abstractmethod
    def find_by_id(self, article_id) -> object | None:
        pass

    @abstractmethod
    def save(self, article) -> object:
        pass

    @abstractmethod
    def update(self, article: dict) -> object:
        pass

    @abstractmethod
    def find_all(self, page_number=None, page_size=None) -> List[object]:
        pass

    @abstractmethod
    def find_total_articles(self) -> int:
        pass

    @abstractmethod
    def bulk_create(self, articles: List[dict]) -> List[object]:
        pass

    @abstractmethod
    def find_articles_by_ids(self, ids: List[str], page: int = 1, page_size: int = 10) -> Tuple[List[object], int]:
        pass

    @abstractmethod
    def find_most_relevant_articles_by_topic(self, topic: str):
        pass

    @abstractmethod
    def find_articles_by_filter_years(self, filter_type: str, filter_years: List[str], ids: List[str]) -> List[object]:
        pass

    @abstractmethod
    def find_years_by_articles(self, ids: List[str]) -> List[object]:
        pass

