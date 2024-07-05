from apps.dashboards.application.services.author_service import AuthorService


class AuthorTopicsYearUseCase:
    def __init__(self, author_service: AuthorService):
        self.author_service = author_service

    def execute(self, scopus_id):
        return self.author_service.get_author_topics_year_contribution_by_id(scopus_id=scopus_id)
