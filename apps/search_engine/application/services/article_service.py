from neomodel import db

from apps.search_engine.domain.entities.article import Article


class ArticleService:
    def get_total_articles(self) -> int:
        query = "MATCH (a:Article) RETURN count(a) AS total"
        results, meta = db.cypher_query(query)
        total_articles = results[0][0]
        return total_articles

    def get_paginated_articles(self, page_number, page_size):
        skip = (page_number - 1) * page_size
        query = f"MATCH (a:Article) RETURN a SKIP {skip} LIMIT {page_size}"
        results, meta = db.cypher_query(query)
        articles = [Article.inflate(row[0]) for row in results]
        return articles
