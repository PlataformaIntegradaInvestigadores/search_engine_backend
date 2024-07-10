from apps.dashboards.application.services.affiliation_service import AffiliationService


class AffiliationsYearUseCase:
    def __init__(self, affiliations_service: AffiliationService):
        self.affiliations_service = affiliations_service

    def execute(self, year):
        return self.affiliations_service.get_affiliations_by_year(year=year)
