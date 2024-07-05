from abc import ABC, abstractmethod


class PopulateRepository(ABC):
    @abstractmethod
    def populate_author(self):
        pass

    @abstractmethod
    def populate_country(self):
        pass

    @abstractmethod
    def get_articles_topics_dict(self):
        pass

    @abstractmethod
    def get_authors_dict(self):
        pass

    @abstractmethod
    def get_affiliations_dict(self):
        pass

