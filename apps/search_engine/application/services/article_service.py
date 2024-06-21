from typing import List

from neomodel import db

from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.repositories.article_repository import ArticleRepository


class ArticleService(ArticleRepository):
    def bulk_create(self, articles: List[dict]) -> List[Article]:
        try:
            return Article.get_or_create(*articles)
        except Exception as e:
            raise ValueError(f"Error creating articles: {e}")

    def get_total_articles(self) -> int:
        query = "MATCH (a:Article) RETURN count(a) AS total"
        results, meta = db.cypher_query(query)
        total_articles = results[0][0]
        return total_articles

    def find_all(self, page_number=1, page_size=10) -> List[Article]:
        skip = (page_number - 1) * page_size
        query = f"MATCH (a:Article) RETURN a SKIP {skip} LIMIT {page_size}"
        results, meta = db.cypher_query(query)
        articles = [Article.inflate(row[0]) for row in results]
        return articles

    def update(self, article: dict) -> Article:
        article = Article.nodes.create_or_update(article)
        return article

    def save(self, article) -> Article:
        article = Article(**article)
        article.save()
        return article

    def find_by_id(self, article_id) -> Article | None:
        article = Article.nodes.get_or_none(article_id=article_id)
        return article
