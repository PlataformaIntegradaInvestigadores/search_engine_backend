from apps.dashboards.domain.entities.affiliation import Affiliation
from apps.dashboards.domain.entities.affiliation_topics_acumulated import AffiliationTopicsAcumulated
from apps.dashboards.domain.entities.affiliation_topics_year import AffiliationTopicsYear
from apps.dashboards.domain.entities.affiliation_year import AffiliationYear
from apps.dashboards.domain.entities.affiliation_year_acumulated import AffiliationAcumulated
from apps.dashboards.domain.repositories.affiliation_repository import AffiliationRepository


class AffiliationService(AffiliationRepository):
    def get_affiliations_by_year(self, year):
        return AffiliationYear.objects(year=year).order_by('-total_articles')[:20]

    def get_affiliation_year(self, scopus_id, year):
        return AffiliationYear.objects.get(scopus_id=scopus_id, year=year)

    def get_affiliation_year_acumulated(self, scopus_id, year):
        return AffiliationAcumulated.objects.get(scopus_id=scopus_id, year=year)

    def get_affiliation_topic(self, scopus_id, year):
        return AffiliationTopicsYear.objects.get(scopus_id=scopus_id, year=year)

    def get_affiliation_topics_acumulated(self, scopus_id, year):
        return AffiliationTopicsAcumulated.objects.get(scopus_id=scopus_id, year=year)

    def get_affiliation(self, scopus_id):
        return Affiliation.objects.get(scopus_id=scopus_id)

    def get_top_affiliations(self, year):
        return AffiliationAcumulated.objects(year=year).order_by('-total_articles')[:30]
