from apps.search_engine.domain.services.author_service import AuthorService


class RetrieveAuthorUseCase:
    def __init__(self, scopus_id: int):
        self.scopus_id = scopus_id

    def execute(self):
        return AuthorService.get_author_by_scopus_id(self.scopus_id)