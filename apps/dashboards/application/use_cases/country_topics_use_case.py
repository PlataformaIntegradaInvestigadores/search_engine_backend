from apps.dashboards.application.services.country_service import CountryService


class CountryTopicsUseCase:
    def __init__(self, country_service: CountryService):
        self.country_service = country_service

    def execute(self, number_top):
        return self.country_service.get_topics(number_top=number_top)
