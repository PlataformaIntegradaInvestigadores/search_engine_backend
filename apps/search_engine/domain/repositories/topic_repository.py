from abc import ABC, abstractmethod
from typing import List


class TopicRepository(ABC):
    @abstractmethod
    def find_by_id(self, topic_id) -> object:
        pass

    @abstractmethod
    def find_by_article_id(self, article_id) -> List[object]:
        pass

    @abstractmethod
    def find_by_author_id(self, author_id) -> List[object]:
        pass

    @abstractmethod
    def save(self, topic) -> object:
        pass

    @abstractmethod
    def update(self, topic) -> object:
        pass

    def get_all(self) -> List[object]:
        pass
