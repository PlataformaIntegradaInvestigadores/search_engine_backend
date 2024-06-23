from apps.search_engine.domain.repositories.author_repository import AuthorRepository


class ListAllAuthorsUseCase:
    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository

    def execute(self, page_size=10, page=1):
        return self.author_repository.get_all(page_size=page_size, page=page)
