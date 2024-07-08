from apps.scopus_integration.domain.repositories.AuthorRepositoryPort import AuthorRepositoryPort
from apps.search_engine.domain.entities.author import Author


class AuthorServicePort(AuthorRepositoryPort):
    def find_no_updated(self):
        try:
            authors = Author.nodes.filter(updated=False)
            return authors
        except Exception as e:
            raise Exception("Error during get all_authors: " + str(e))
