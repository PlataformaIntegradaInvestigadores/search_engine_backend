from abc import ABC, abstractmethod


class AuthorRepository(ABC):
    @abstractmethod
    def get_by_id(self, scopus_id):
        pass

    @abstractmethod
    def get_author_topics_by_id(self, scopus_id):
        pass

    @abstractmethod
    def get_author_year_contribution_by_id(self, scopus_id):
        pass

    @abstractmethod
    def get_author_topics_year_contribution_by_id(self, scopus_id):
        pass
