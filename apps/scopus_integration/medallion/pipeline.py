from typing import Dict

from apps.scopus_integration.medallion.gold import GoldAggregator
from apps.scopus_integration.medallion.repository import ScopusMedallionRepository
from apps.scopus_integration.medallion.silver import SilverTransformer


class ScopusMedallionPipeline:
    def __init__(self, repository: ScopusMedallionRepository | None = None) -> None:
        self.repository = repository or ScopusMedallionRepository()

    def run_silver(self) -> Dict[str, int]:
        return SilverTransformer(self.repository).transform()

    def run_gold(self) -> Dict[str, int]:
        return GoldAggregator(self.repository).build()

    def get_gold_ml_documents(self):
        return GoldAggregator(self.repository).get_ml_documents()
