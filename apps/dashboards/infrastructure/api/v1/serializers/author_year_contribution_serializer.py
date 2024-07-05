from rest_framework_mongoengine.serializers import DocumentSerializer

from apps.dashboards.domain.entities.author_year_contribution import AuthorYearContribution


class AuthorYearContributionSerializer(DocumentSerializer):
    class Meta:
        model = AuthorYearContribution
        fields = ['scopus_id', 'year', 'total_articles']
