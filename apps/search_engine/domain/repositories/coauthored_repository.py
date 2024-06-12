from abc import ABC, abstractmethod


class CoauthoredRepository(ABC):

    @abstractmethod
    def save(self, coauthored) -> object:
        pass
