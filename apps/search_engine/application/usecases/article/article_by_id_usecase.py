from apps.search_engine.domain.repositories.article_repository import ArticleRepository


class ArticleByIdUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(self, article_id):
        return self.article_repository.find_by_id(article_id)
