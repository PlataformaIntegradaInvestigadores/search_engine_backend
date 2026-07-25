from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List

from apps.scopus_integration.medallion.repository import ScopusMedallionRepository
from apps.scopus_integration.medallion.schemas import GoldDashboardMetrics, GoldGraphEntity, GoldMlFeature


class GoldAggregator:
    def __init__(self, repository: ScopusMedallionRepository) -> None:
        self.repository = repository

    def build(self) -> Dict[str, int]:
        ml_features: List[Dict[str, Any]] = []
        graph_entities: List[Dict[str, Any]] = []
        articles = list(self.repository.iter_silver_articles())

        for article in articles:
            authors = list(self.repository.get_silver_authors(article.get("author_ids", [])).values())
            affiliations = list(self.repository.get_silver_affiliations(article.get("affiliation_ids", [])).values())
            topics = [topic for topic in article.get("topics", []) if topic]
            text = " ".join(
                part
                for part in [
                    article.get("title", ""),
                    article.get("abstract", ""),
                    " ".join(topics),
                    " ".join(author.get("indexed_name", "") for author in authors),
                    " ".join(affiliation.get("name", "") for affiliation in affiliations),
                ]
                if part
            ).strip()

            ml_features.append(
                GoldMlFeature(
                    doc_id=article["scopus_id"],
                    doc_type="article",
                    title=article.get("title", ""),
                    abstract=article.get("abstract", ""),
                    topics=topics,
                    authors=authors,
                    affiliations=affiliations,
                    text=text,
                ).model_dump()
            )
            graph_entities.append(self._graph_entity(article, authors, affiliations, topics).model_dump())

        metrics = self._dashboard_metrics(articles)
        return {
            "gold_ml_features": self.repository.replace_gold_ml_features(ml_features),
            "gold_graph_entities": self.repository.replace_gold_graph_entities(graph_entities),
            "gold_dashboard_metrics": self._save_metrics(metrics),
        }

    def get_ml_documents(self) -> List[Dict[str, str]]:
        return [
            {"doc_id": item["doc_id"], "text": item.get("text", "")}
            for item in self.repository.iter_gold_ml_features()
            if item.get("doc_id") and item.get("text")
        ]

    @staticmethod
    def _graph_entity(article: Dict[str, Any], authors: List[Dict[str, Any]], affiliations: List[Dict[str, Any]], topics: List[str]) -> GoldGraphEntity:
        relationships = []
        for author in authors:
            relationships.append({"from": author["author_id"], "to": article["scopus_id"], "type": "WROTE"})
        for affiliation in affiliations:
            relationships.append({"from": article["scopus_id"], "to": affiliation["affiliation_id"], "type": "HAS_AFFILIATION"})
        for topic in topics:
            relationships.append({"from": article["scopus_id"], "to": topic, "type": "USES"})

        return GoldGraphEntity(
            article={
                "scopus_id": article["scopus_id"],
                "title": article.get("title", ""),
                "abstract": article.get("abstract", ""),
                "publication_year": article.get("publication_year"),
                "doi": article.get("doi", ""),
            },
            authors=authors,
            affiliations=affiliations,
            topics=[{"name": topic} for topic in topics],
            relationships=relationships,
        )

    @staticmethod
    def _dashboard_metrics(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        by_year = Counter(article.get("publication_year") for article in articles if article.get("publication_year"))
        by_topic = Counter(topic for article in articles for topic in article.get("topics", []) if topic)
        affiliation_counts = Counter(
            affiliation_id
            for article in articles
            for affiliation_id in article.get("affiliation_ids", [])
            if affiliation_id
        )
        country_counts = defaultdict(int)
        for article in articles:
            for country in article.get("countries", []):
                if country:
                    country_counts[country] += 1

        return GoldDashboardMetrics(
            generated_at=datetime.utcnow(),
            totals={"articles": len(articles)},
            by_year=[{"year": year, "count": count} for year, count in sorted(by_year.items())],
            by_country=[{"country": country, "count": count} for country, count in sorted(country_counts.items())],
            by_affiliation=[
                {"affiliation_id": affiliation_id, "count": count}
                for affiliation_id, count in affiliation_counts.most_common()
            ],
            by_topic=[{"topic": topic, "count": count} for topic, count in by_topic.most_common()],
        ).model_dump()

    def _save_metrics(self, metrics: Dict[str, Any]) -> int:
        self.repository.save_dashboard_metrics(metrics)
        return 1
