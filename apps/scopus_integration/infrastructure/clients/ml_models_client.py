from typing import Any, Dict, List

import requests
from django.conf import settings


class MLModelsClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = (base_url or settings.ML_MODELS_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.ML_MODELS_TIMEOUT_SECONDS

    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def models(self) -> Dict[str, Any]:
        return self._request("GET", "/v1/models")

    def vectorize(self, text: str, translate_to_english: bool = True, clean_text: bool = True) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/v1/vectorize",
            json={
                "text": text,
                "translate_to_english": translate_to_english,
                "clean_text": clean_text,
            },
        )

    def keywords(self, text: str, top_n: int = 10) -> Dict[str, Any]:
        return self._request("POST", "/v1/keywords", json={"text": text, "top_n": top_n})

    def build_tfidf(self, documents: List[Dict[str, Any]], version: str = "v10.0") -> Dict[str, Any]:
        return self._request(
            "POST",
            "/v1/tfidf/build",
            json={"documents": documents, "version": version, "persist_corpus": True},
        )

    def search_tfidf(self, query: str, version: str = "v10.0", top_k: int = 10) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/v1/tfidf/search",
            json={"query": query, "version": version, "top_k": top_k},
        )

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        response = requests.request(method, f"{self.base_url}{path}", timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json()
