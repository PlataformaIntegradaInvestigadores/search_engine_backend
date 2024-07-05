from abc import ABC, abstractmethod


class CountryRepository(ABC):
    @abstractmethod
    def get_acumulated_by_year(self, year):
        pass

    @abstractmethod
    def get_year(self, year):
        pass

    @abstractmethod
    def get_topics_acumulated_by_year(self, topic, year):
        pass

    @abstractmethod
    def get_topics_by_year(self, topic, year):
        pass

    @abstractmethod
    def get_topics(self):
        pass

    @abstractmethod
    def get_top_topics(self, number_top):
        pass

    @abstractmethod
    def get_last_years(self):
        pass

    @abstractmethod
    def get_top_topics_by_year(self, year):
        pass
