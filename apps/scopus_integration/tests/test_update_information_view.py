from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory

from apps.scopus_integration.infrastructure.api.v1.views.update_information_views import (
    UpdateInformationViewSet,
)


class _GoldAuthorUpdater:
    def execute(self):
        return 21


class _LegacyAuthorRepository:
    def authors_no_updated(self):
        raise AssertionError("Legacy Scopus author retrieval must not run in Medallion mode")


class _CorpusObserver:
    def __init__(self):
        self.delete_calls = 0

    def delete_corpus(self):
        self.delete_calls += 1

    def delete_model(self):
        self.delete_calls += 1


class UpdateInformationViewSetTests(SimpleTestCase):
    @override_settings(USE_ML_MODELS_SERVICE=True)
    def test_author_update_publishes_gold_without_deleting_ml_artifacts(self):
        view = UpdateInformationViewSet()
        observer = _CorpusObserver()
        view.author_repository = _LegacyAuthorRepository()
        view.gold_author_updater = _GoldAuthorUpdater()
        view.model_corpus_observer = observer
        request = APIRequestFactory().post("/author-information/", {}, format="json")

        response = view.update_author_information(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {"success": True, "message": "21 Authors were updated successfully"},
        )
        self.assertEqual(observer.delete_calls, 0)
