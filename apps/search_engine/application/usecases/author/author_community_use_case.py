from typing import List

from apps.search_engine.domain.repositories.author_repository import AuthorRepository


class AuthorsCommunityUseCase:
    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository

    def execute(self, authors_ids: List[str]):
        return self.author_repository.find_community(authors_ids)
