from apps.search_engine.application.services.author_service import AuthorService


class ListAllAuthorsUseCase:
    def __init__(self, author_service: AuthorService):
        self.author_service = author_service

    def execute(self, page_size=10, page=1):
        return self.author_service.get_all(page_size=page_size, page=page)
