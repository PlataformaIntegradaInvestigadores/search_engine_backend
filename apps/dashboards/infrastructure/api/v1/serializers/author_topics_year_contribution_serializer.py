from rest_framework_mongoengine.serializers import DocumentSerializer

from apps.dashboards.domain.entities.author_topics_year_contribution import AuthorTopicsYearContribution


class AuthorTopicsYearContributionSerializer(DocumentSerializer):
    class Meta:
        model = AuthorTopicsYearContribution
        fields = ['scopus_id', 'topic_name', 'year', 'total_articles']
