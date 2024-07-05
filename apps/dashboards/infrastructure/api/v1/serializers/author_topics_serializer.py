from rest_framework_mongoengine.serializers import DocumentSerializer

from apps.dashboards.domain.entities.author_topics import AuthorTopics


class AuthorTopicsSerializer(DocumentSerializer):
    class Meta:
        model = AuthorTopics
        fields = ['scopus_id', 'topic_name', 'total_articles']
