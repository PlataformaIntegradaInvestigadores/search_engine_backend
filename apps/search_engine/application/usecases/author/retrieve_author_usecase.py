from apps.search_engine.application.services.author_service import AuthorService


class RetrieveAuthorUseCase:

    def __init__(self, author_service: AuthorService):
        self.author_service = author_service

    def execute(self, scopus_id: int):
        return self.author_service.find_by_id(scopus_id)
