# from typing import List, Tuple
# from neomodel import db, Q
# from apps.search_engine.application.utils.tfidf import Model
# from apps.search_engine.domain.entities.article import Article
# from apps.search_engine.domain.repositories.article_repository import ArticleRepository
# import logging

# logger = logging.getLogger(__name__)

# class ArticleService(ArticleRepository):
#     def find_articles_by_author(self, author_id: str) -> List[object]:
#         try:
#             query = "MATCH (a:Article)-[:WROTE]-(au:Author) WHERE au.scopus_id = $author_id RETURN a"
#             results, meta = db.cypher_query(query, {"author_id": author_id})
#             articles = [Article.inflate(row[0]) for row in results]
#             return articles
#         except Exception as e:
#             raise Exception(f"Error finding articles by author: {e}")

#     def articles_count(self) -> int:
#         try:
#             query = "MATCH (a:Article) RETURN count(a) "
#             results, meta = db.cypher_query(query)
#             total_articles = results[0][0]
#             return total_articles
#         except Exception as e:
#             raise ValueError(f"Error finding total articles: {e}")


#     def find_articles_by_ids(self, ids: List[str], page: int = 1, page_size: int = 10) -> Tuple[List[object], int]:
#         try:
#             skip = (page - 1) * page_size
#             ids_integer = [str(w) for w in ids]  

#             # Obtener total de artículos
#             query_to_find_articles = f"MATCH (a:Article) WHERE a.scopus_id IN {ids_integer} RETURN count(a) AS total"
#             total_results, meta = db.cypher_query(query_to_find_articles)
#             total_articles = total_results[0][0]

#             # Log para depuración
#             logger.info(f"Buscando artículos con IDs: {ids_integer}")

#             # Modificar la consulta para usar la misma dirección que funciona en tu prueba
#             query = (f"""
#                 MATCH (a:Article) 
#                 WHERE a.scopus_id IN {ids_integer}
#                 WITH a
#                 OPTIONAL MATCH (a)<-[:WROTE]-(au:Author)  // Cambiado para especificar dirección explícita
#                 WITH a, COLLECT(DISTINCT au) as authors
#                 OPTIONAL MATCH (a)-[:BELONGS_TO]-(aff:Affiliation)
#                 WITH a, authors, COLLECT(DISTINCT aff) as affiliations
#                 OPTIONAL MATCH (a)-[:USES]-(t:Topic)
#                 WITH a, authors, affiliations, COLLECT(DISTINCT t.name) as topics,
#                     [au in authors | au.auth_name] as author_names,
#                     [aff in affiliations | aff.name] as affiliation_names
#                 RETURN a,
#                     SIZE(authors) as author_count,
#                     SIZE(affiliations) as affiliation_count,
#                     author_names,
#                     affiliation_names,
#                     topics
#                 ORDER BY a.publication_date DESC 
#                 SKIP {skip} LIMIT {page_size}
#             """)
            
#             results, meta = db.cypher_query(query)
            
#             # Log detallado para depuración
#             logger.info("\nResultados de la consulta:")
#             for row in results:
#                 logger.info(f"\nArtículo: {row[0].scopus_id}")
#                 logger.info(f"Author Count: {row[1]}")
#                 logger.info(f"Author Names: {row[3]}")
            
#             articles = []
#             for row in results:
#                 article = Article.inflate(row[0])
#                 article_dict = {
#                     'scopus_id': article.scopus_id,
#                     'title': article.title,
#                     'publication_date': article.publication_date,
#                     'abstract': article.abstract,
#                     'author_count': int(row[1]),
#                     'affiliation_count': int(row[2]),
#                     'authors': row[3] if row[3] else [],
#                     'affiliations': row[4] if row[4] else [],
#                     'topics': row[5] if row[5] else [],
#                     'relevance': 0.0
#                 }
#                 logger.info(f"\nProcesando artículo: {article_dict['scopus_id']}")
#                 logger.info(f"Author count final: {article_dict['author_count']}")
#                 logger.info(f"Authors final: {article_dict['authors']}")
#                 articles.append(article_dict)

#             return articles, total_articles

#         except Exception as e:
#             logger.error(f"Error en find_articles_by_ids: {str(e)}")
#             raise Exception(f"Error finding articles by ids: {e}")
        
#     # En article_service.py
#     def find_most_relevant_articles_by_topic(self, topic: str):
#         logger.info(f"Buscando artículos más relevantes por tema: {topic}")
#         try:
#             m = Model("article")
#             # Esto devuelve solo IDs y scores
#             df = m.get_most_relevant_docs_by_topic_v2(topic, None)
            
#             # Necesitamos obtener la información completa de cada artículo
#             article_list = []
#             for scopus_id, score in df.items():
#                 try:
#                     # Obtener el artículo completo de Neo4j
#                     article = self.find_by_id(str(scopus_id))
#                     if article:
#                         # Convertir a diccionario y agregar el score
#                         article_dict = {
#                             'scopus_id': article.scopus_id,
#                             'title': article.title,
#                             'publication_date': article.publication_date,
#                             'author_count': article.author_count,
#                             'affiliation_count': article.affiliation_count,
#                             'relevance': float(score)
#                         }
#                         article_list.append(article_dict)
#                 except Exception as e:
#                     print(f"Error processing article {scopus_id}: {e}")
#                     continue

#             return article_list
#         except Exception as e:
#             raise Exception(f"Error finding most relevant articles by topic: {e}")
    
#     def find_articles_by_filter_years(self, filter_type: str, filter_years: List[str], ids: List[str]) -> List[object]:
#         try:
#             # Cambiar este cmportamiento dependiendo de la bd

#             ids = [f'"{str(w)}"' for w in ids]
#             ids_str = ', '.join(map(str, ids))
#             filter_years_str = ' OR '.join([f'a.publication_date CONTAINS "{year}"' for year in filter_years])

#             if filter_type == 'include':
#                 query = f"""
#                 MATCH (a:Article)
#                 WHERE a.scopus_id IN [{ids_str}] AND ({filter_years_str})
#                 RETURN a
#                 """
#             else:
#                 query = f"""
#                 MATCH (a:Article)
#                 WHERE a.scopus_id IN [{ids_str}] AND NOT ({filter_years_str})
#                 RETURN a
#                 """
#             results, _ = db.cypher_query(query)
#             articles = [Article.inflate(row[0]) for row in results]
#             return articles
#         except Exception as e:
#             raise Exception(f"Error finding articles by filter years: {e}")

#     def find_years_by_articles(self, ids: List[str]) -> List[object]:
#         try:
#             # Comment
#             query = f"MATCH (a:Article) WHERE a.scopus_id IN {ids} RETURN a"
#             results, meta = db.cypher_query(query)
#             articles = [Article.inflate(row[0]) for row in results]
#             years = []
#             for article in articles:
#                 years.append(article.publication_date)
#             return years
#         except Exception as e:
#             raise Exception(f"Error getting years by articles: {e}")

#     def bulk_create(self, articles: List[dict]) -> List[Article]:
#         try:
#             return Article.get_or_create(*articles)
#         except Exception as e:
#             raise ValueError(f"Error creating articles: {e}")

#     def find_total_articles(self) -> int:
#         try:
#             query = "MATCH (a:Article) RETURN count(a) AS total"
#             results, meta = db.cypher_query(query)
#             total_articles = results[0][0]
#             return total_articles
#         except Exception as e:
#             raise ValueError(f"Error finding total articles: {e}")

#     def find_all(self, page_number=1, page_size=10) -> List[Article]:
#         try:
#             skip = (page_number - 1) * page_size
#             query = f"MATCH (a:Article) RETURN a SKIP {skip} LIMIT {page_size}"
#             results, meta = db.cypher_query(query)
#             articles = [Article.inflate(row[0]) for row in results]
#             return articles
#         except Exception as e:
#             raise Exception(f"Error finding all articles: {e}")

#     def update(self, article: dict) -> Article:
#         try:
#             article = Article.nodes.create_or_update(article)
#             return article
#         except Exception as e:
#             raise Exception(f"Error updating article: {e}")

#     def save(self, article) -> Article:
#         try:
#             article = Article(**article)
#             article.save()
#             return article
#         except Exception as e:
#             raise Exception(f"Error saving article: {e}")

#     def find_by_id(self, article_id) -> Article | None:
#         try:
#             article = Article.nodes.get_or_none(scopus_id=article_id)
#             return article
#         except Exception as e:
#             raise Exception(f"Error finding article by id: {e}")

#     def find_authors_by_article(self, article_id: str) -> List[object]:
#         try:
#             query = (
#                 "MATCH (a:Article {scopus_id: $article_id}) "
#                 "OPTIONAL MATCH (a)-[:WROTE]-(au:Author) "
#                 "RETURN collect(DISTINCT {scopusId: au.scopus_id, name: au.auth_name})"
#             )
#             results, meta = db.cypher_query(query, {'article_id': article_id})
#             authors = [row[0] for row in results]
#             return authors
#         except Exception as e:
#             raise Exception(f"Error finding authors by article: {e}")




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
            # Asegúrate de que los IDs estén en el formato correcto
            ids_integer = [str(w) for w in ids]  

            # Obtener total de artículos
            query_to_find_articles = f"MATCH (a:Article) WHERE a.scopus_id IN {ids_integer} RETURN count(a) AS total"
            total_results, meta = db.cypher_query(query_to_find_articles)
            total_articles = total_results[0][0]

            # Obtener artículos con toda su información
            query = (f"""
                MATCH (a:Article) 
                WHERE a.scopus_id IN {ids_integer} 
                OPTIONAL MATCH (a)-[:WROTE]-(au:Author)
                OPTIONAL MATCH (a)-[:BELONGS_TO]-(aff:Affiliation)
                RETURN a, 
                    count(DISTINCT au) as author_count,
                    count(DISTINCT aff) as affiliation_count,
                    collect(DISTINCT au.auth_name) as authors,
                    collect(DISTINCT aff.name) as affiliations
                ORDER BY a.publication_date DESC 
                SKIP {skip} LIMIT {page_size}
            """)
            
            results, meta = db.cypher_query(query)
            
            # Procesar resultados
            articles = []
            for row in results:
                article = Article.inflate(row[0])
                article_dict = {
                    'scopus_id': article.scopus_id,
                    'title': article.title,
                    'publication_date': article.publication_date,
                    'author_count': row[1],
                    'affiliation_count': row[2],
                    'authors': row[3],
                    'affiliations': row[4]
                }
                articles.append(article_dict)

            return articles, total_articles
        except Exception as e:
            raise Exception(f"Error finding articles by ids: {e}")    
        
    # En article_service.py
    def find_most_relevant_articles_by_topic(self, topic: str):
        try:
            m = Model("article")
            # Esto devuelve solo IDs y scores
            df = m.get_most_relevant_docs_by_topic_v2(topic, None)
            
            # Necesitamos obtener la información completa de cada artículo
            article_list = []
            for scopus_id, score in df.items():
                try:
                    # Obtener el artículo completo de Neo4j
                    article = self.find_by_id(str(scopus_id))
                    if article:
                        # Convertir a diccionario y agregar el score
                        article_dict = {
                            'scopus_id': article.scopus_id,
                            'title': article.title,
                            'publication_date': article.publication_date,
                            'author_count': article.author_count,
                            'affiliation_count': article.affiliation_count,
                            'relevance': float(score)
                        }
                        article_list.append(article_dict)
                except Exception as e:
                    print(f"Error processing article {scopus_id}: {e}")
                    continue

            return article_list
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
