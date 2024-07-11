from typing import List

from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.repositories.article_repository import ArticleRepository


class MostRelevantArticlesUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(self, topic: str, page: int, size: int):
        df = self.article_repository.find_most_relevant_articles_by_topic(topic)
        years = self.article_repository.find_years_by_articles(df.index.to_list())

        return df.index.to_list(), years
