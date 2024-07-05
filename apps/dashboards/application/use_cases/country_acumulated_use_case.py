from apps.dashboards.application.services.country_service import CountryService


class CountryAcumulatedUseCase:
    def __init__(self, country_service: CountryService):
        self.country_service = country_service

    def execute(self, year):
        return self.country_service.get_acumulated_by_year(year=year)
