from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from pymongo import ASCENDING, MongoClient, UpdateOne

from apps.scopus_integration.medallion.config import MedallionConfig


class ScopusMedallionRepository:
    def __init__(self, mongo_uri: Optional[str] = None, db_name: Optional[str] = None) -> None:
        self.client = MongoClient(mongo_uri or MedallionConfig.resolve_mongo_uri())
        self.db = self.client[db_name or MedallionConfig.mongo_db_name]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.raw_articles.create_index([("dc:identifier", ASCENDING)], unique=True, sparse=True)
        self.raw_authors.create_index([("author_id", ASCENDING)], unique=True, sparse=True)
        self.raw_affiliations.create_index([("afid", ASCENDING)], unique=True, sparse=True)
        self.cursors.create_index([("query", ASCENDING), ("date_range", ASCENDING)], unique=True)
        self.silver_articles.create_index([("scopus_id", ASCENDING)], unique=True)
        self.silver_authors.create_index([("author_id", ASCENDING)], unique=True)
        self.silver_affiliations.create_index([("affiliation_id", ASCENDING)], unique=True)
        self.gold_ml_features.create_index([("doc_id", ASCENDING)], unique=True)

    @property
    def raw_articles(self):
        return self.db[MedallionConfig.raw_articles_collection]

    @property
    def raw_authors(self):
        return self.db[MedallionConfig.raw_authors_collection]

    @property
    def raw_affiliations(self):
        return self.db[MedallionConfig.raw_affiliations_collection]

    @property
    def cursors(self):
        return self.db[MedallionConfig.cursors_collection]

    @property
    def silver_articles(self):
        return self.db[MedallionConfig.silver_articles_collection]

    @property
    def silver_authors(self):
        return self.db[MedallionConfig.silver_authors_collection]

    @property
    def silver_affiliations(self):
        return self.db[MedallionConfig.silver_affiliations_collection]

    @property
    def gold_ml_features(self):
        return self.db[MedallionConfig.gold_ml_features_collection]

    @property
    def gold_graph_entities(self):
        return self.db[MedallionConfig.gold_graph_entities_collection]

    @property
    def gold_dashboard_metrics(self):
        return self.db[MedallionConfig.gold_dashboard_metrics_collection]

    def upsert_raw_articles(self, articles: Iterable[Dict[str, Any]], metadata: Dict[str, Any]) -> int:
        operations = []
        for article in articles:
            identifier = article.get("dc:identifier") or article.get("identifier")
            if not identifier:
                continue
            payload = {
                **article,
                "_metadata": {
                    **metadata,
                    "source": "scopus",
                    "fetched_at": metadata.get("fetched_at") or datetime.utcnow(),
                    "payload_version": MedallionConfig.payload_version,
                },
            }
            operations.append(UpdateOne({"dc:identifier": identifier}, {"$set": payload}, upsert=True))
        if not operations:
            return 0
        self.raw_articles.bulk_write(operations, ordered=False)
        return len(operations)

    def save_cursor(self, query: str, date_range: str, cursor: str) -> None:
        self.cursors.update_one(
            {"query": query, "date_range": date_range},
            {"$set": {"cursor": cursor, "updated_at": datetime.utcnow()}},
            upsert=True,
        )

    def get_cursor(self, query: str, date_range: str) -> Optional[str]:
        document = self.cursors.find_one({"query": query, "date_range": date_range})
        return document.get("cursor") if document else None

    def upsert_raw_author(self, author: Dict[str, Any]) -> None:
        author_id = author.get("author_id") or author.get("authid") or author.get("dc:identifier")
        if author_id:
            self.raw_authors.update_one({"author_id": str(author_id)}, {"$set": author}, upsert=True)

    def upsert_raw_affiliation(self, affiliation: Dict[str, Any]) -> None:
        afid = affiliation.get("afid") or affiliation.get("affiliation_id")
        if afid:
            self.raw_affiliations.update_one({"afid": str(afid)}, {"$set": affiliation}, upsert=True)

    def iter_raw_articles(self):
        return self.raw_articles.find({})

    def iter_silver_articles(self):
        return self.silver_articles.find({})

    def get_silver_authors(self, ids: List[str]) -> Dict[str, Dict[str, Any]]:
        return {item["author_id"]: item for item in self.silver_authors.find({"author_id": {"$in": ids}})}

    def get_silver_affiliations(self, ids: List[str]) -> Dict[str, Dict[str, Any]]:
        return {item["affiliation_id"]: item for item in self.silver_affiliations.find({"affiliation_id": {"$in": ids}})}

    def upsert_silver_articles(self, articles: Iterable[Dict[str, Any]]) -> int:
        return self._bulk_upsert(self.silver_articles, "scopus_id", articles)

    def upsert_silver_authors(self, authors: Iterable[Dict[str, Any]]) -> int:
        return self._bulk_upsert(self.silver_authors, "author_id", authors)

    def upsert_silver_affiliations(self, affiliations: Iterable[Dict[str, Any]]) -> int:
        return self._bulk_upsert(self.silver_affiliations, "affiliation_id", affiliations)

    def replace_gold_ml_features(self, documents: Iterable[Dict[str, Any]]) -> int:
        self.gold_ml_features.delete_many({"source": "scopus"})
        return self._bulk_upsert(self.gold_ml_features, "doc_id", documents)

    def replace_gold_graph_entities(self, documents: Iterable[Dict[str, Any]]) -> int:
        self.gold_graph_entities.delete_many({"source": "scopus"})
        operations = [
            UpdateOne({"article.scopus_id": item["article"]["scopus_id"]}, {"$set": item}, upsert=True)
            for item in documents
        ]
        if not operations:
            return 0
        self.gold_graph_entities.bulk_write(operations, ordered=False)
        return len(operations)

    def save_dashboard_metrics(self, metrics: Dict[str, Any]) -> None:
        self.gold_dashboard_metrics.insert_one(metrics)

    def iter_gold_ml_features(self):
        return self.gold_ml_features.find({})

    @staticmethod
    def _bulk_upsert(collection, key: str, documents: Iterable[Dict[str, Any]]) -> int:
        operations = [
            UpdateOne({key: item[key]}, {"$set": item}, upsert=True)
            for item in documents
            if item.get(key)
        ]
        if not operations:
            return 0
        collection.bulk_write(operations, ordered=False)
        return len(operations)

    def close(self) -> None:
        self.client.close()
