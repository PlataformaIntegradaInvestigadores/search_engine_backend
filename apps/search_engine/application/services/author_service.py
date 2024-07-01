from typing import List

from neomodel import db, Q

from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.repositories.author_repository import AuthorRepository
from unidecode import unidecode
from apps.search_engine.application.utils.tfidf import Model


class AuthorService(AuthorRepository):

    def find_most_relevant_authors_by_topic(self, topic: str, authors_number: int):
        try:
            m = Model("author")
            authors = m.get_most_relevant_docs_by_topic_v2(topic, authors_number)
            return authors
        except Exception as e:
            raise Exception(f"Error finding most relevant authors by topic: {e}")

    def find_community(self, authors_ids: List[str]):
        try:
            print("Type of authors_ids on service: ", type(authors_ids))
            query = Q(scopus_id__in=authors_ids)
            nodes = Author.nodes.filter(query)
            auth_list_str = ', '.join([f'"{w}"' for w in authors_ids])
            # Consulta para obtener enlaces
            print("auth_list_str: ", auth_list_str)
            query_links = f"""
                  WITH [{auth_list_str}] as authList
                  MATCH (au1:Author)-[r:CO_AUTHORED]-(au2:Author)
                  WHERE au1.scopus_id IN authList AND au2.scopus_id IN authList AND au1 > au2
                  RETURN collect({{source: au1.scopus_id, target: au2.scopus_id, 
                      collabStrength: toFloat(r.collab_strength)}}) as links
                  """
            result = db.cypher_query(query_links)
            print("Result: ", result)
            # Ensure we only unpack two values
            result_links, meta = result
            links = result_links[0]

            return {"nodes": nodes, "links": links, "size_nodes": len(nodes), "size_links": len(links)}
        except Exception as e:
            raise Exception(f"Error finding community: {e}")

    def find_authors_by_affiliation_filter(self, filter_type: str, affiliations_ids: List[str],
                                           authors_ids: List[str]) -> List[object]:
        try:
            # filter_type = '' if filter_type == 'include' else 'not'
            query = Q(scopus_id__in=authors_ids)
            if filter_type == 'include':
                authors = Author.nodes.filter(query, affiliations__scopus_id__in=affiliations_ids)
            else:
                authors = Author.nodes.filter(query, ~Q(affiliations__scopus_id__in=affiliations_ids))
                return authors
        except Exception as e:
            raise Exception(f"Error finding authors by affiliation filter: {e}")

    def find_authors_by_query(self, name: str, page_size=1, page=10) -> (List[object], int):
        name = unidecode(name).strip().lower()
        skip = (page - 1) * page_size
        query = f"""
                MATCH (au:Author) 
                WHERE  toLower(au.first_name) CONTAINS '{name}' or 
                toLower(au.last_name) CONTAINS '{name}' or 
                toLower(au.first_name) + " " + toLower(au.last_name) CONTAINS '{name}' or
                toLower(au.last_name) + " " + toLower(au.first_name) CONTAINS '{name}' or  
                toLower(au.auth_name) CONTAINS '{name}' or 
                toLower(au.initials) CONTAINS '{name}' or 
                toLower(au.email) CONTAINS '{name}'or 
                au.scopus_id CONTAINS '{name}'
                RETURN count(au) as total
        """
        results, meta = db.cypher_query(query)
        total = results[0][0]
        query = f"""
                MATCH (au:Author) 
                WHERE  toLower(au.first_name) CONTAINS '{name}' or 
                toLower(au.last_name) CONTAINS '{name}' or 
                toLower(au.first_name) + " " + toLower(au.last_name) CONTAINS '{name}' or
                toLower(au.last_name) + " " + toLower(au.first_name) CONTAINS '{name}' or  
                toLower(au.auth_name) CONTAINS '{name}' or 
                toLower(au.initials) CONTAINS '{name}' or 
                toLower(au.email) CONTAINS '{name}' or 
                au.scopus_id CONTAINS '{name}'
                RETURN au SKIP {skip} LIMIT {page_size}
                                                                                                """
        results, meta = db.cypher_query(query)
        authors = [Author.inflate(row[0]) for row in results]
        return authors, total

    def find_all(self, page_size=None, page=None) -> List[Author]:
        try:
            skip = (page - 1) * page_size
            query = f"MATCH (a:Author) RETURN a SKIP {skip} LIMIT {page_size}"
            results, meta = db.cypher_query(query)
            authors = [Author.inflate(row[0]) for row in results]
            return authors
        except Exception as e:
            raise Exception(f"Error finding all authors: {e}")

    def find_by_id(self, scopus_id) -> Author:
        try:
            return Author.nodes.get(scopus_id=scopus_id)
        except Exception as e:
            raise Exception(f"Error finding author by id: {e}")

    def save(self, author) -> Author:
        pass

    def update(self, author) -> Author:
        pass

    def bulk_create(self, authors: List[dict]) -> List[Author]:
        try:
            return Author.get_or_create(*authors)
        except Exception as e:
            raise Exception(f"Error bulk creating authors: {e}")
