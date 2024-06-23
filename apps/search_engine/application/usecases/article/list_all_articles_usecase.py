from apps.search_engine.domain.repositories.article_repository import ArticleRepository


class ListAllArticlesUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository  # Inject the service

    def execute(self, page_number, page_size):
        return self.article_repository.find_all(page_number, page_size)
