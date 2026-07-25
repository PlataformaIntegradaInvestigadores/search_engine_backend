from datetime import datetime
from typing import Any, Dict, Optional

import requests
from django.conf import settings

from apps.scopus_integration.medallion.config import MedallionConfig
from apps.scopus_integration.medallion.repository import ScopusMedallionRepository


class ScopusClient:
    def __init__(self, api_key: str, inst_token: str = "", session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "X-ELS-APIKey": api_key,
            }
        )
        if inst_token and settings.SCOPUS_USE_INSTTOKEN:
            self.session.headers.update({"X-ELS-Insttoken": inst_token})

    def get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = self.session.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()


class ScopusSearchService:
    search_url = "https://api.elsevier.com/content/search/scopus"

    def __init__(self, client: ScopusClient, repository: ScopusMedallionRepository) -> None:
        self.client = client
        self.repository = repository

    def fetch(
        self,
        query: str = MedallionConfig.default_query,
        date_range: str = "",
        page_size: int = 25,
        max_pages: Optional[int] = None,
        resume: bool = True,
    ) -> Dict[str, Any]:
        cursor = self.repository.get_cursor(query, date_range) if resume else "*"
        cursor = cursor or "*"
        pages = 0
        total_saved = 0

        while True:
            payload = self.client.get(
                self.search_url,
                {
                    "query": query,
                    "cursor": cursor,
                    "count": page_size,
                    "view": "COMPLETE",
                    "date": date_range or None,
                },
            )
            search_results = payload.get("search-results", {})
            entries = search_results.get("entry", [])
            next_cursor = (
                search_results.get("cursor", {}).get("@next")
                or search_results.get("cursor", {}).get("next")
                or cursor
            )

            total_saved += self.repository.upsert_raw_articles(
                entries,
                {
                    "query": query,
                    "date_range": date_range,
                    "cursor": cursor,
                    "fetched_at": datetime.utcnow(),
                },
            )
            self.repository.save_cursor(query, date_range, next_cursor)

            pages += 1
            if not entries or next_cursor == cursor or (max_pages and pages >= max_pages):
                break
            cursor = next_cursor

        return {"pages": pages, "total_saved": total_saved, "last_cursor": cursor}
