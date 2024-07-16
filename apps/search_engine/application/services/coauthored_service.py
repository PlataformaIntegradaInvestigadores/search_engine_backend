from neomodel import DoesNotExist

from apps.search_engine.domain.repositories.author_repository import AuthorRepository
from apps.search_engine.domain.repositories.coauthored_repository import CoAuthoredRepository


class CoAuthoredService(CoAuthoredRepository):
    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository

    def save(self, coauthored) -> object:
        pass

    def find_coauthors_by_id(self, author_id: str):
        try:
            author = self.author_repository.find_by_id(author_id)
            links = []
            nodes = author.co_authors
            # Recorre los coautores y las relaciones
            for co_author in author.co_authors:
                rel = author.co_authors.relationship(co_author)
                collab_strength = rel.collab_strength

                link = {
                    'source': int(author.scopus_id),
                    'target': int(co_author.scopus_id),
                    'collabStrength': float(collab_strength)
                }
                links.append(link)

            return nodes, links
        except DoesNotExist as e:
            raise e
        except Exception as e:
            raise Exception("An error occurred while trying to find coauthors by id.", str(e))
