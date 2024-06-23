from apps.search_engine.domain.repositories.article_repository import ArticleRepository
from typing import List


class ArticlesBulkCreateUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(self, articles: List[dict]):
        return self.article_repository.bulk_create(articles)
