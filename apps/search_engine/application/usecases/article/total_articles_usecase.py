from apps.search_engine.application.services.article_service import ArticleService


class TotalArticlesUseCase:
    def __init__(self, article_service: ArticleService):
        self.article_service = article_service

    def execute(self) -> int:
        return self.article_service.get_total_articles()
