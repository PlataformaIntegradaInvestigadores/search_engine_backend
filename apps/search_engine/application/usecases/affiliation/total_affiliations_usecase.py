from apps.search_engine.domain.repositories.affiliation_repository import AffiliationRepository


class TotalAffiliationsUseCase:
    def __init__(self, affiliation_repository: AffiliationRepository):
        self.affiliation_repository = affiliation_repository

    def execute(self) -> int:
        return self.affiliation_repository.get_total_affiliations()
