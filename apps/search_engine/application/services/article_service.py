from typing import List, Tuple

from neomodel import db, Q

from apps.search_engine.application.utils.tfidf import Model
from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.repositories.article_repository import ArticleRepository


class ArticleService(ArticleRepository):
    def find_articles_by_author(self, author_id: str) -> List[object]:
        try:
            query = "MATCH (a:Article)-[:WROTE]-(au:Author) WHERE au.scopus_id = $author_id RETURN a"
            results, meta = db.cypher_query(query, {"author_id": author_id})
            articles = [Article.inflate(row[0]) for row in results]
            return articles
        except Exception as e:
            raise Exception(f"Error finding articles by author: {e}")

    def articles_count(self) -> int:
        try:
            query = "MATCH (a:Article) RETURN count(a) "
            results, meta = db.cypher_query(query)
            total_articles = results[0][0]
            return total_articles
        except Exception as e:
            raise ValueError(f"Error finding total articles: {e}")

    def find_articles_by_ids(self, ids: List[str], page: int = 1, page_size: int = 10) -> Tuple[List[object], int]:
        try:
            skip = (page - 1) * page_size
            # Cast to int the list of ids
            # ids_integer = [int(w) for w in ids]  # Join IDs into a quoted string
            # Retrieve total articles found on that list
            ids_integer = [w for w in ids]
            query_to_find_articles = f"MATCH (a:Article) WHERE a.scopus_id IN {ids_integer} RETURN count(a) AS total"
            total_results, meta = db.cypher_query(query_to_find_articles)
            total_articles = total_results[0][0]

            # Retrieve articles found on that list
            query = (f"MATCH (a:Article) WHERE a.scopus_id IN {ids_integer} RETURN a ORDER BY a.publication_date DESC "
                     f"SKIP {skip} LIMIT {page_size}")
            results, meta = db.cypher_query(query)
            articles = [Article.inflate(row[0]) for row in results]

            return articles, total_articles
        except Exception as e:
            raise Exception(f"Error finding articles by ids: {e}")

    def find_most_relevant_articles_by_topic(self, topic: str):
        try:
            m = Model("article")
            return m.get_most_relevant_docs_by_topic_v2(topic, None)
        except Exception as e:
            raise Exception(f"Error finding most relevant articles by topic: {e}")

    def find_articles_by_filter_years(self, filter_type: str, filter_years: List[str], ids: List[str]) -> List[object]:
        try:
            # Cambiar este cmportamiento dependiendo de la bd

            ids = [f'"{str(w)}"' for w in ids]
            ids_str = ', '.join(map(str, ids))
            filter_years_str = ' OR '.join([f'a.publication_date CONTAINS "{year}"' for year in filter_years])

            if filter_type == 'include':
                query = f"""
                MATCH (a:Article)
                WHERE a.scopus_id IN [{ids_str}] AND ({filter_years_str})
                RETURN a
                """
            else:
                query = f"""
                MATCH (a:Article)
                WHERE a.scopus_id IN [{ids_str}] AND NOT ({filter_years_str})
                RETURN a
                """
            results, _ = db.cypher_query(query)
            articles = [Article.inflate(row[0]) for row in results]
            return articles
        except Exception as e:
            raise Exception(f"Error finding articles by filter years: {e}")

    def find_years_by_articles(self, ids: List[str]) -> List[object]:
        try:
            # Comment
            query = f"MATCH (a:Article) WHERE a.scopus_id IN {ids} RETURN a"
            results, meta = db.cypher_query(query)
            articles = [Article.inflate(row[0]) for row in results]
            years = []
            for article in articles:
                years.append(article.publication_date)
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

    def find_authors_by_article(self, article_id: str) -> List[object]:
        try:
            query = (
                "MATCH (a:Article {scopus_id: $article_id}) "
                "OPTIONAL MATCH (a)-[:WROTE]-(au:Author) "
                "RETURN collect(DISTINCT {scopusId: au.scopus_id, name: au.auth_name})"
            )
            results, meta = db.cypher_query(query, {'article_id': article_id})
            authors = [row[0] for row in results]
            return authors
        except Exception as e:
            raise Exception(f"Error finding authors by article: {e}")
