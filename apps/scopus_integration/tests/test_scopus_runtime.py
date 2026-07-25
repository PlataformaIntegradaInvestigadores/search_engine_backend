import json
import os
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.application.services.search_scopus_service import RetrieveScopusData
from apps.scopus_integration.infrastructure.clients.ml_models_client import MLModelsClient


class _FakeCustomRequest:
    def __init__(self):
        self.params = None

    def do_get(self, endpoint, params):
        self.params = params
        return {"search-results": {"opensearch:totalResults": "77412"}}


class _SuccessfulResponse:
    status_code = 200
    text = json.dumps({"ok": True})


class _FakeSession:
    def __init__(self):
        self.headers = None

    def mount(self, *args, **kwargs):
        return None

    def get(self, url, headers):
        self.headers = headers
        return _SuccessfulResponse()


class RetrieveScopusDataTests(SimpleTestCase):
    def test_total_articles_uses_search_view_available_to_api_key(self):
        service = RetrieveScopusData()
        fake_request = _FakeCustomRequest()
        service.custom_request = fake_request

        total = service.get_total_articles_from_scopus()

        self.assertEqual(total, "77412")
        self.assertEqual(fake_request.params["count"], 1)
        self.assertNotIn("view", fake_request.params)
        self.assertNotIn("field", fake_request.params)
        self.assertNotIn("cursor", fake_request.params)


class ScopusClientTests(SimpleTestCase):
    @override_settings(SCOPUS_USE_AUTHTOKEN=False, SCOPUS_USE_INSTTOKEN=False)
    def test_expired_authtoken_is_not_sent_when_disabled(self):
        fake_session = _FakeSession()
        env = {
            "X_ELS_APIKEY": "api-key",
            "X_ELS_AUTHTOKEN": "expired-token",
            "X_ELS_INSTTOKEN": "",
        }

        with patch.dict(os.environ, env, clear=False), patch(
            "apps.scopus_integration.application.services.scopus_client.requests.Session",
            return_value=fake_session,
        ):
            ScopusClient().exec_request("https://example.test/author")

        self.assertEqual(fake_session.headers["X-ELS-APIKey"], "api-key")
        self.assertNotIn("X-ELS-Authtoken", fake_session.headers)


class MLModelsClientTests(SimpleTestCase):
    def test_models_returns_remote_artifact_status(self):
        payload = {
            "tfidf": {
                "version": "v10.0",
                "model_exists": True,
                "corpus_exists": True,
            }
        }
        client = MLModelsClient(base_url="http://models.test")

        with patch.object(client, "_request", return_value=payload):
            try:
                result = client.models()
            except AttributeError as error:
                self.fail(f"MLModelsClient.models is required: {error}")

        self.assertEqual(result, payload)
