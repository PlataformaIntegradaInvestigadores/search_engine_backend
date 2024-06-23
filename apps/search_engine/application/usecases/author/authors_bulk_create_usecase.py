from apps.search_engine.application.services.author_service import AuthorService
from apps.search_engine.domain.repositories.author_repository import AuthorRepository


class AuthorsBulkCreateUseCase:
    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository

    def execute(self, authors: dict):
        return self.author_repository.bulk_create(*authors)
