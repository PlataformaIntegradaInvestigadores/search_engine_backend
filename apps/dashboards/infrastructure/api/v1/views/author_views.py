from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dashboards.application.services.author_service import AuthorService
from apps.dashboards.application.use_cases.author_by_id_use_case import AuthorByIdUseCase
from apps.dashboards.application.use_cases.author_topics_by_id_use_case import AuthorTopicsByIdUseCase
from apps.dashboards.application.use_cases.author_topics_year_by_id import AuthorTopicsYearUseCase
from apps.dashboards.application.use_cases.author_year_use_case import AuthorYearUseCase
from apps.dashboards.infrastructure.api.v1.serializers.author_serializer import AuthorSerializer
from apps.dashboards.infrastructure.api.v1.serializers.author_topics_serializer import AuthorTopicsSerializer
from apps.dashboards.infrastructure.api.v1.serializers.author_topics_year_contribution_serializer import AuthorTopicsYearContributionSerializer
from apps.dashboards.infrastructure.api.v1.serializers.author_year_contribution_serializer import \
    AuthorYearContributionSerializer


class AuthorViews(viewsets.ModelViewSet):
    author_service = AuthorService()

    def retrieve(self, request, *args, **kwargs):
        scopus_id = (request.query_params.get('scopus_id'))
        author_use_case = AuthorByIdUseCase(author_service=self.author_service)
        author_topics = author_use_case.execute(scopus_id=scopus_id)
        serializer = AuthorSerializer(author_topics)
        data = serializer.data
        return Response({'author': scopus_id, 'author-info': data})

    @action(detail=False, methods=['get'])
    def get_topics(self, request):
        scopus_id = (request.query_params.get('scopus_id'))
        author_topics_use_case = AuthorTopicsByIdUseCase(author_service=self.author_service)
        author_topics = author_topics_use_case.execute(scopus_id=scopus_id)
        serializer = AuthorTopicsSerializer(author_topics, many=True)
        data = serializer.data
        return Response({'author': scopus_id, 'author-topics': data})

    @action(detail=False, methods=['get'])
    def get_topics_year(self, request):
        scopus_id = (request.query_params.get('scopus_id'))
        author_topics_year_use_case = AuthorTopicsYearUseCase(author_service=self.author_service)
        author_topics_year = author_topics_year_use_case.execute(scopus_id=scopus_id)
        serializer = AuthorTopicsYearContributionSerializer(author_topics_year, many=True)
        data = serializer.data
        return Response({'author': scopus_id, 'author-topics-year': data})

    @action(detail=False, methods=['get'])
    def get_year(self, request):
        scopus_id = (request.query_params.get('scopus_id'))
        author_year_use_case = AuthorYearUseCase(author_service=self.author_service)
        author_year = author_year_use_case.execute(scopus_id=scopus_id)
        serializer = AuthorYearContributionSerializer(author_year, many=True)
        data = serializer.data
        return Response({'author': scopus_id, 'author-year': data})
