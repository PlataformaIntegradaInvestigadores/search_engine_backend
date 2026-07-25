import requests
import os
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.conf import settings

from apps.scopus_integration.application.services.model_corpus_observer_service import ModelCorpusObserverService
import threading
import logging

from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.application.usecases.scopus_integration_usecase import ScopusIntegrationUseCase
from apps.scopus_integration.medallion.bronze import ScopusClient as MedallionScopusClient, ScopusSearchService
from apps.scopus_integration.medallion.config import MedallionConfig
from apps.scopus_integration.medallion.repository import ScopusMedallionRepository

logger = logging.getLogger('django')


def _extract_scopus_error(error: requests.HTTPError) -> tuple[str, dict]:
    try:
        content = error.response.json()
    except Exception:
        content = {"detail": str(error)}

    message = (
        content.get('error-response', {}).get('error-message')
        or content.get('service-error', {}).get('status', {}).get('statusText')
        or content.get('message')
        or str(error)
    )
    return message, content


class ScopusIntegrationViewSet(viewsets.ModelViewSet):
    lock = threading.Lock()
    scopus_client = ScopusClient()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_corpus_observer = ModelCorpusObserverService()

    @extend_schema(
        summary='Integrate Scopus data',
        description='This endpoint integrates Scopus data.',
        tags=['Scopus Integration'],
    )
    def list(self, request, *args, **kwargs):
        try:
            logger.log(logging.INFO, "Starting the Scopus integration .....")
            if settings.USE_ML_MODELS_SERVICE:
                api_key = os.environ.get("X_ELS_APIKEY")
                if not api_key:
                    return Response(
                        {"success": False, "message": "X_ELS_APIKEY is required to extract Scopus data."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not self.lock.acquire(blocking=False):
                    return Response(
                        {"success": False, "message": "Scopus extraction is already running."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

                extraction_options = {
                    "api_key": api_key,
                    "inst_token": os.environ.get("X_ELS_INSTTOKEN", ""),
                    "query": request.query_params.get("query", MedallionConfig.default_query),
                    "date_range": request.query_params.get("date", "2010-2020"),
                    "page_size": self._safe_int(request.query_params.get("count"), 25),
                    "max_pages": self._safe_int(
                        request.query_params.get("max_pages"),
                        settings.SCOPUS_EXTRACTION_DEFAULT_MAX_PAGES,
                    ),
                    "resume": request.query_params.get("resume", "true").lower() != "false",
                }
                threading.Thread(
                    target=self._run_medallion_extraction,
                    kwargs=extraction_options,
                    daemon=True,
                ).start()
                return Response(
                    {
                        "success": True,
                        "message": "Scopus extraction started.",
                        "max_pages": extraction_options["max_pages"],
                        "page_size": extraction_options["page_size"],
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            scopus_integration = ScopusIntegrationUseCase(scopus_client=self.scopus_client)
            scopus_integration.execute()
            return Response({"success": True}, status=status.HTTP_200_OK)
        except requests.HTTPError as e:
            error_message, error_content = _extract_scopus_error(e)
            logger.log(logging.ERROR, error_message)
            status_code = e.response.status_code if e.response is not None else status.HTTP_502_BAD_GATEWAY
            response_status = status.HTTP_400_BAD_REQUEST if status_code < 500 else status.HTTP_502_BAD_GATEWAY
            return Response({
                "success": False,
                "message": error_message,
                "code": status_code,
                "error": error_content
            }, status=response_status)
        except Exception as e:
            logger.log(logging.ERROR, str(e))
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if not settings.USE_ML_MODELS_SERVICE:
                self.model_corpus_observer.delete_corpus()
                self.model_corpus_observer.delete_model()
            # self.lock.release()

    @classmethod
    def _run_medallion_extraction(
        cls,
        api_key: str,
        inst_token: str,
        query: str,
        date_range: str,
        page_size: int,
        max_pages: int,
        resume: bool,
    ) -> None:
        try:
            medallion_client = MedallionScopusClient(api_key=api_key, inst_token=inst_token)
            repository = ScopusMedallionRepository()
            service = ScopusSearchService(client=medallion_client, repository=repository)
            result = service.fetch(
                query=query,
                date_range=date_range,
                page_size=page_size,
                max_pages=max_pages,
                resume=resume,
            )
            logger.info("Scopus extraction finished: %s", result)
        except requests.HTTPError as error:
            message, content = _extract_scopus_error(error)
            logger.error("Scopus extraction failed: %s | %s", message, content)
        except Exception as error:
            logger.exception("Scopus extraction failed unexpectedly: %s", error)
        finally:
            cls.lock.release()

    @staticmethod
    def _safe_int(value, default: int) -> int:
        try:
            parsed = int(value)
            return parsed if parsed > 0 else default
        except (TypeError, ValueError):
            return default
