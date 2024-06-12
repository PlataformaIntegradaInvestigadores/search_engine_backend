from typing import List

from apps.search_engine.domain.entities.topic import Topic
from apps.search_engine.domain.repositories.topic_repository import TopicRepository


class TopicService(TopicRepository):
    def find_by_id(self, topic_id) -> Topic:
        pass

    def find_by_article_id(self, article_id) -> List[Topic]:
        pass

    def find_by_author_id(self, author_id) -> List[Topic]:
        pass

    def save(self, topic) -> Topic:
        pass

    def update(self, topic) -> Topic:
        pass

    def get_all(self) -> list[Topic]:
        return Topic.nodes.all()
