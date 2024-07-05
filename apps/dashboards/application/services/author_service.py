from apps.dashboards.domain.entities.author import Author
from apps.dashboards.domain.entities.author_topics import AuthorTopics
from apps.dashboards.domain.entities.author_topics_year_contribution import AuthorTopicsYearContribution
from apps.dashboards.domain.entities.author_year_contribution import AuthorYearContribution
from apps.dashboards.domain.repositories.author_repository import AuthorRepository


class AuthorService(AuthorRepository):
    def get_by_id(self, scopus_id):
        return Author.objects.get(scopus_id=scopus_id)

    def get_author_topics_by_id(self, scopus_id):
        return AuthorTopics.objects(scopus_id=scopus_id)

    def get_author_year_contribution_by_id(self, scopus_id):
        return AuthorYearContribution.objects(scopus_id=scopus_id)

    def get_author_topics_year_contribution_by_id(self, scopus_id):
        return AuthorTopicsYearContribution.objects(scopus_id=scopus_id)


