from apps.search_engine.application.services.article_service import ArticleService

class ListAllArticlesUseCase:
    # Inject the repository
    def __init__(self, article_service: ArticleService):
        self.article_repository = article_service  # Inject the service

    def execute(self, page_number, page_size):
        return self.article_repository.find_all(page_number, page_size)
