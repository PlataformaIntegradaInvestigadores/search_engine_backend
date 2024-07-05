from rest_framework_mongoengine.serializers import DocumentSerializer

from apps.dashboards.domain.entities.author import Author


class AuthorSerializer(DocumentSerializer):
    class Meta:
        model = Author
        fields = ['scopus_id', 'total_articles']
