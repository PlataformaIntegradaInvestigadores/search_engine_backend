from neomodel import db

from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.application.usecases.author_retrieval_usecase import AuthorRetrieval
from apps.scopus_integration.domain.repositories.AuthorRepositoryPort import AuthorRepositoryPort
from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.repositories.author_repository import AuthorRepository


class UpdateAuthorInformationUseCase:
    def __init__(self, author_repository: AuthorRepository, client: ScopusClient):
        self.author_repository = author_repository
        self.client = client

    def execute(self):
        try:
            authors = self.author_repository.authors_no_updated()
            batch_size = 25
            total_authors = len(authors)

            for i in range(0, total_authors, batch_size):
                batch_authors = authors[i:i + batch_size]
                author_retrievals = [AuthorRetrieval(author_id=author_instance.scopus_id) for author_instance in
                                     batch_authors]

                for retrieval in author_retrievals:
                    try:
                        retrieval.execute(self.client)
                    except Exception as e:
                        print(f"Error executing retrieval for retrieval: {e}")
                        continue

                for author_instance, retrieval in zip(batch_authors, author_retrievals):
                    try:
                        retrieval_info = retrieval.result[0]
                        Author.update_from_json(author_data=retrieval_info)
                    except Exception as e:
                        print(f"Error updating author {author_instance.id}: {e}")
                        continue

            return total_authors
        except Exception as e:
            raise Exception("Error during execution: " + str(e))
