from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboards.application.services.populate_service import PopulateService
from apps.dashboards.application.use_cases.populate_use_case import PopulateUseCase


class PopulateView(APIView):
    populate_service = PopulateService()

    def post(self, request):
        populate_use_case = PopulateUseCase(populate_service=self.populate_service)
        populate_use_case.execute()
        return Response({'message': 'author populated'})
