from abc import ABC, abstractmethod


class ProvinceRepository(ABC):
    @abstractmethod
    def get_provinces_info(self):
        pass

    @abstractmethod
    def get_province_year(self, name, year):
        pass

    @abstractmethod
    def get_province_acumulated(self, name, year):
        pass

    @abstractmethod
    def get_provinces_year(self, year):
        pass

    @abstractmethod
    def get_province_topic_year(self, year):
        pass

    @abstractmethod
    def get_province_topic_acumulated(self, year):
        pass
