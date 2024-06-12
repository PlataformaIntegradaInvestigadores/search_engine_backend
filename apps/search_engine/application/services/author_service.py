from apps.search_engine.domain.entities.author import Author


class AuthorService:
    def get_author_by_scopus_id(scopus_id: int) -> Author:
        return Author.nodes.get(scopus_id=scopus_id)
