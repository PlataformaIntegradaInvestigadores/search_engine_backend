from typing import List

from neomodel import db

from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.repositories.author_repository import AuthorRepository


class AuthorService(AuthorRepository):

    def get_all(self, page_size=None, page=None) -> List[Author]:
        skip = (page - 1) * page_size
        query = f"MATCH (a:Author) RETURN a SKIP {skip} LIMIT {page_size}"
        results, meta = db.cypher_query(query)
        authors = [Author.inflate(row[0]) for row in results]
        return authors

    def find_by_id(self, scopus_id) -> Author:
        return Author.nodes.get(scopus_id=scopus_id)

    def save(self, author) -> Author:
        pass

    def update(self, author) -> Author:
        pass

    def bulk_create(self, authors: List[dict]) -> List[Author]:
        return Author.get_or_create(*authors)
