from abc import ABC, abstractmethod


class CoAuthoredRepository(ABC):

    @abstractmethod
    def save(self, coauthored) -> object:
        pass

    @abstractmethod
    def find_coauthors_by_id(self, author_id: str):
        pass
