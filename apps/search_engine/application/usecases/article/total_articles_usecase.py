from apps.search_engine.domain.repositories.article_repository import ArticleRepository


class TotalArticlesUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(self) -> int:
        return self.article_repository.find_total_articles()
