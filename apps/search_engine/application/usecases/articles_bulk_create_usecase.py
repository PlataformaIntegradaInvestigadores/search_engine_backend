from apps.search_engine.application.services.article_service import ArticleService


class ArticlesBulkCreateUseCase:
    def __init__(self, article_service: ArticleService):
        self.article_service = article_service

    def execute(self, articles: list[dict]):
        return self.article_service.bulk_create(articles)
