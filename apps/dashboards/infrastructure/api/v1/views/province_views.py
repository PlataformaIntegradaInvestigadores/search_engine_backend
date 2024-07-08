from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dashboards.application.services.province_service import ProvinceService
from apps.dashboards.application.use_cases.get_provinces import ProvincesUseCase
from apps.dashboards.infrastructure.api.v1.serializers.province_serializer import ProvinceSerializer


class ProvinceViews(viewsets.ModelViewSet):
    province_service = ProvinceService()

    @action(detail=False, methods=['get'])
    def get_provinces(self, request):
        provinces_use_case = ProvincesUseCase(province_service=self.province_service)
        data_provinces = provinces_use_case.execute()
        serializer = ProvinceSerializer(data_provinces, many=True)
        response = serializer.data
        return Response(response)
