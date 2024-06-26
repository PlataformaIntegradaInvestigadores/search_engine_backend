from typing import List

from neomodel import db, Q

from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.repositories.article_repository import ArticleRepository


class ArticleService(ArticleRepository):
    def find_articles_by_ids(self, ids: List[str], page: int = 1, page_size: int = 10) -> List[object]:
        try:
            skip = (page - 1) * page_size
            query = f"MATCH (a:Article) WHERE a.article_id IN {ids} RETURN a SKIP {skip} LIMIT {page_size}"
            results, meta = db.cypher_query(query)
            articles = [Article.inflate(row[0]) for row in results]
            return articles
        except Exception as e:
            raise Exception(f"Error finding articles by ids: {e}")

    def find_most_relevant_articles_by_topic(self, topic: str):
        try:
            pass
        except Exception as e:
            raise Exception(f"Error finding most relevant articles by topic: {e}")

    def find_articles_by_filter_years(self, filter_type: str, filter_years: List[str], ids: List[str]) -> List[object]:
        try:
            # filter_type = '' if filter_type == 'include' else 'not'
            query = Q(article_id__in=ids)
            if filter_type == 'include':
                articles = Article.nodes.filter(query, publication_date__in=filter_years)
            else:
                articles = Article.nodes.filter(query, ~Q(publication_date__in=filter_years))
            return articles
        except Exception as e:
            raise Exception(f"Error finding articles by filter years: {e}")

    def find_years_by_articles(self, ids: List[str]) -> List[object]:
        try:
            articles = Article.nodes.filter(article_id__in=ids)
            years = articles.values_list('publication_date', flat=True)
            return years
        except Exception as e:
            raise Exception(f"Error getting years by articles: {e}")

    def bulk_create(self, articles: List[dict]) -> List[Article]:
        try:
            return Article.get_or_create(*articles)
        except Exception as e:
            raise ValueError(f"Error creating articles: {e}")

    def find_total_articles(self) -> int:
        try:
            query = "MATCH (a:Article) RETURN count(a) AS total"
            results, meta = db.cypher_query(query)
            total_articles = results[0][0]
            return total_articles
        except Exception as e:
            raise ValueError(f"Error finding total articles: {e}")

    def find_all(self, page_number=1, page_size=10) -> List[Article]:
        try:
            skip = (page_number - 1) * page_size
            query = f"MATCH (a:Article) RETURN a SKIP {skip} LIMIT {page_size}"
            results, meta = db.cypher_query(query)
            articles = [Article.inflate(row[0]) for row in results]
            return articles
        except Exception as e:
            raise Exception(f"Error finding all articles: {e}")

    def update(self, article: dict) -> Article:
        try:
            article = Article.nodes.create_or_update(article)
            return article
        except Exception as e:
            raise Exception(f"Error updating article: {e}")

    def save(self, article) -> Article:
        try:
            article = Article(**article)
            article.save()
            return article
        except Exception as e:
            raise Exception(f"Error saving article: {e}")

    def find_by_id(self, article_id) -> Article | None:
        try:
            article = Article.nodes.get_or_none(scopus_id=article_id)
            return article
        except Exception as e:
            raise Exception(f"Error finding article by id: {e}")
