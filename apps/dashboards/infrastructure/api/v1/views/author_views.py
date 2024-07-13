from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dashboards.domain.entities.affiliation_year import AffiliationYear
from apps.dashboards.domain.entities.author_topics import AuthorTopics
from apps.dashboards.domain.entities.author_year import AuthorYear
from apps.dashboards.infrastructure.api.v1.serializers.author_year_serializer import AuthorYearSerializer
from apps.search_engine.application.services.author_service import AuthorService


class AuthorViews(viewsets.ModelViewSet):

    @action(detail=False, methods=['get'])
    def get_author_years(self, request):
        scopus_id = (request.query_params.get('scopus_id'))
        author = AuthorYear.objects(scopus_id=scopus_id).filter(year__gt=1999).order_by('year')
        serializer = AuthorYearSerializer(author, many=True)
        data = serializer.data
        return Response(data)

    @action(detail=False, methods=['get'])
    def get_topics(self, request):
        scopus_id = (request.query_params.get('scopus_id'))
        author_topics = AuthorTopics.objects(scopus_id=scopus_id).filter(topic_name__ne=" ").order_by('-total_articles')
        response_data = [
            {
                "text": topic['topic_name'],
                "size": topic['total_articles']
            }
            for topic in author_topics
        ]

        return Response(response_data)
