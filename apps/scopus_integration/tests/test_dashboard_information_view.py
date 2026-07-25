from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory

from apps.scopus_integration.infrastructure.api.v1.views.dashboard_information_views import (
    DashboardInformationViewSet,
)


class _RemoteModelsClient:
    def models(self):
        return {
            "tfidf": {
                "version": "v10.0",
                "model_exists": True,
                "corpus_exists": True,
            }
        }


class _MissingLocalArtifacts:
    def verify_model_path_exists(self):
        return False

    def verify_corpus_path_exists(self):
        return False


class DashboardInformationViewSetTests(SimpleTestCase):
    @override_settings(USE_ML_MODELS_SERVICE=True)
    def test_tfidf_status_comes_from_ml_microservice_in_service_mode(self):
        view = DashboardInformationViewSet()
        view.ml_models_client = _RemoteModelsClient()
        view.model_corpus_observer = _MissingLocalArtifacts()
        request = APIRequestFactory().get("/tfidf_model_corpus/")

        response = view.tfidf_model_corpus(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"model": True, "corpus": True})
