from apps.dashboards.application.services.affiliation_service import AffiliationService


class AffiliationsUseCase:
    def __init__(self, affiliations_service: AffiliationService):
        self.affiliations_service = affiliations_service

    def execute(self):
        return self.affiliations_service.get_top_affiliations()
