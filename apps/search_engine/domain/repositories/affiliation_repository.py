from abc import ABC, abstractmethod
from typing import List


class AffiliationRepository(ABC):
    @abstractmethod
    def find_by_id(self, affiliation_id) -> object:
        pass

    @abstractmethod
    def find_by_name(self, affiliation_name) -> List[object]:
        pass

    @abstractmethod
    def save(self, affiliation) -> object:
        pass

    @abstractmethod
    def update(self, affiliation) -> object:
        pass
