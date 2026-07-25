import logging
import threading

from drf_spectacular import openapi
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboards.application.services.populate_service import PopulateService
from apps.dashboards.application.use_cases.populate_use_case import PopulateUseCase

logger = logging.getLogger('django')


class PopulateView(APIView):
    lock = threading.Lock()
    populate_service = PopulateService()

    @extend_schema(
        description="Populate the datalake with data",
        responses={
            202: OpenApiResponse(description="Datalake population started", examples={'application/json': {'success': True, 'message': 'Analytics DB population started'}}),
            429: OpenApiResponse(description="Datalake population already running"),
            500: OpenApiResponse(description="Internal Server Error", examples={'application/json': {'error': 'error message'}})
        },
        tags=['Data Population']
    )
    def post(self, request):
        if not self.lock.acquire(blocking=False):
            return Response(
                {
                    'error': 'Analytics DB population is already running',
                    'message': 'Analytics DB population is already running',
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            threading.Thread(
                target=self._run_population,
                args=(self.populate_service,),
                daemon=True,
            ).start()
            return Response(
                {
                    'success': True,
                    'message': 'Analytics DB population started',
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception as e:
            self.lock.release()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def _run_population(cls, populate_service):
        try:
            PopulateUseCase(populate_service=populate_service).execute()
            logger.info("Analytics DB population finished.")
        except Exception:
            logger.exception("Analytics DB population failed.")
        finally:
            cls.lock.release()
