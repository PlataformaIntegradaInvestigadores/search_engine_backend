from apps.search_engine.domain.repositories.author_repository import AuthorRepository


class RetrieveAuthorUseCase:

    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository

    def execute(self, scopus_id: int):
        return self.author_repository.find_by_id(scopus_id)
