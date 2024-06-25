from abc import ABC, abstractmethod


class CorpusRepository(ABC):

    @abstractmethod
    def get_corpus_by_article(self):
        pass

    @abstractmethod
    def get_corpus_by_author(self):
        pass
