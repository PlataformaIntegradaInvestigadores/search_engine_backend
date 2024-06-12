from apps.search_engine.application.services.author_service import AuthorService


class AuthorsBulkCreateUseCase:
    def __init__(self, author_service: AuthorService):
        self.author_service = author_service

    def execute(self, authors: dict):
        return self.author_service.bulk_create(*authors)
