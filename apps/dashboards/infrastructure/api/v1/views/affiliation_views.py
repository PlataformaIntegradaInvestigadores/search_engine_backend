from mongoengine import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dashboards.application.services.affiliation_service import AffiliationService
from apps.dashboards.application.use_cases.get_affiliations_acumulated_use_case import AffiliationsAcumulatedUseCase
from apps.dashboards.application.use_cases.get_affiliations_use_case import AffiliationsUseCase
from apps.dashboards.application.use_cases.get_affiliations_year_acumulated import AffiliationsYearUseCase
from apps.dashboards.domain.entities.affiliation import Affiliation
from apps.dashboards.domain.entities.affiliation_topics import AffiliationTopics
from apps.dashboards.domain.entities.affiliation_topics_acumulated import AffiliationTopicsAcumulated
from apps.dashboards.domain.entities.affiliation_year import AffiliationYear
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_acumulated_serializer import \
    AffiliationAcumulatedSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_serializer import AffiliationSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_topic_serializer import AffiliationTopicSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_topics_acumulated_serializer import \
    AffiliationTopicAcumulatedSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_topics_serializer import AffiliationTopicsSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_year_serializer import AffiliationYearSerializer


class AffiliationViewSet(viewsets.ModelViewSet):
    affiliation_service = AffiliationService()

    @action(detail=False, methods=['get'])
    def get_top_affiliations(self, request):
        year = (request.query_params.get('year'))
        affiliations_use_case = AffiliationsAcumulatedUseCase(affiliations_service=self.affiliation_service)
        affiliations = affiliations_use_case.execute(year=year)
        serializer = AffiliationAcumulatedSerializer(affiliations, many=True)
        data = serializer.data
        response_data = [
            {
                "text": affiliation['name'],
                "size": affiliation['total_articles']
            }
            for affiliation in data
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_affiliations(self, request):
        affiliations_use_case = AffiliationsUseCase(affiliations_service=self.affiliation_service)
        affiliations = affiliations_use_case.execute()
        serializer = AffiliationSerializer(affiliations, many=True)
        data = serializer.data
        response_data = [
            {
                "text": affiliation['name'],
                "size": affiliation['total_articles']
            }
            for affiliation in data
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_top_affiliations_year(self, request):
        year = (request.query_params.get('year'))
        affiliations_year_use_case = AffiliationsYearUseCase(affiliations_service=self.affiliation_service)
        affiliations = affiliations_year_use_case.execute(year=year)
        serializer = AffiliationYearSerializer(affiliations, many=True)
        data = serializer.data
        response_data = [
            {
                "text": affiliation['name'],
                "size": affiliation['total_articles']
            }
            for affiliation in data
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.GET.get('query', '')
        affiliations = Affiliation.objects.filter(Q(name__icontains=query)).order_by('-total_articles')
        result = [
            {
                'scopus_id': affiliation.scopus_id,
                'name': affiliation.name,
                'total_articles': affiliation.total_articles
            } for affiliation in affiliations
        ]
        return Response(result)

    @action(detail=False, methods=['get'])
    def get_affiliation_years(self, request):
        scopus_id = (request.query_params.get('scopus_id'))
        # year = (request.query_params.get('year'))
        affiliation = AffiliationYear.objects(scopus_id=scopus_id).filter(year__gt=1999).order_by('year')
        serializer = AffiliationYearSerializer(affiliation, many=True)
        data = serializer.data
        return Response(data)

    @action(detail=False, methods=['get'])
    def get_affiliation_topics(self, request):
        scopus_id = (request.query_params.get('scopus_id'))
        # year = (request.query_params.get('year'))
        affiliation_topics = AffiliationTopics.objects(scopus_id=scopus_id).filter(topic_name__ne=" ").order_by(
            '-total_articles')[:20]
        serializer = AffiliationTopicsSerializer(affiliation_topics, many=True)
        data = serializer.data
        response_data = [
            {
                "text": topic['topic_name'],
                "size": topic['total_articles']
            }
            for topic in data
        ]

        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_years(self, request):
        years_use_case = LastYearsUseCase(country_service=self.country_service)
        last_years = years_use_case.execute()
        serializer = CountryYearSerializer(last_years, many=True)
        data = serializer.data
        response_data = [
            {
                'year': cy['year'],
            }
            for cy in data
        ]
        return Response(response_data)