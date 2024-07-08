from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dashboards.application.services.affiliation_service import AffiliationService
from apps.dashboards.application.use_cases.get_affiliations_use_case import AffiliationsUseCase
from apps.dashboards.application.use_cases.get_affiliations_year_acumulated import AffiliationsYearUseCase
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_acumulated_serializer import \
    AffiliationAcumulatedSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_topics_acumulated_serializer import \
    AffiliationTopicAcumulatedSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_year_serializer import AffiliationYearSerializer


class AffiliationViewSet(viewsets.ModelViewSet):
    affiliation_service = AffiliationService()

    @action(detail=False, methods=['get'])
    def get_top_affiliations(self, request):
        year = (request.query_params.get('year'))
        affiliations_use_case = AffiliationsUseCase(affiliations_service=self.affiliation_service)
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

    @action(detail=True, methods=['GET'])
    def get_top_affiliations_year(self, request):
        year = (request.query_params.get('year'))
        affiliations_year_use_case = AffiliationsYearUseCase(affiliations_service=self.affiliation_service)
        affiliations = affiliations_year_use_case.execute(year=year)
        serializer = AffiliationYearSerializer(affiliations, many=True)
        data = serializer.data
        response_data = [
            {
                "text": affiliation['name'],
                "size": affiliation['total-articles']
            }
            for affiliation in data
        ]
        return Response(response_data)

