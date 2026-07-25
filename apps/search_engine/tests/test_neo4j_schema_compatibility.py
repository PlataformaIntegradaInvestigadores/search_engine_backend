from unittest.mock import patch
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory

from apps.search_engine.application.services.article_service import ArticleService
from apps.search_engine.application.services.author_service import AuthorService
from apps.search_engine.domain.entities.affiliation import Affiliation
from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.entities.coauthored import CoAuthored
from apps.search_engine.infrastructure.api.v1.views.article_views import ArticleViewSet
from apps.search_engine.infrastructure.api.v1.serializers.author_serializers import AuthorSerializer


class Neo4jPropertyMappingTests(SimpleTestCase):
    def test_author_api_fields_map_to_new_neo4j_properties(self):
        properties = Author.defined_properties(rels=False)

        self.assertEqual(properties["scopus_id"].db_property, "authid")
        self.assertEqual(properties["first_name"].db_property, "given_name")
        self.assertEqual(properties["last_name"].db_property, "surname")
        self.assertEqual(properties["auth_name"].db_property, "authname")

    def test_affiliation_api_id_maps_to_afid(self):
        properties = Affiliation.defined_properties(rels=False)

        self.assertEqual(properties["scopus_id"].db_property, "afid")

    def test_article_api_fields_map_to_imported_neo4j_schema(self):
        properties = Article.defined_properties(rels=False)

        self.assertEqual(properties["scopus_id"].db_property, "scopus_id")
        self.assertEqual(properties["cited_by_count"].db_property, "cited_by_count")

    def test_coauthor_relation_maps_to_imported_neo4j_schema(self):
        relation = Author.defined_properties(rels=True)["co_authors"]
        properties = CoAuthored.defined_properties()

        self.assertEqual(relation.definition["relation_type"], "COAUTHORED")
        self.assertEqual(properties["shared_pubs"].db_property, "article_count")

    def test_current_affiliation_falls_back_to_related_affiliation(self):
        class Related:
            def all(self):
                return [type("AffiliationStub", (), {"name": "Escuela Politecnica Nacional"})()]

        class EmptyRelated:
            def all(self):
                return []

        author = type(
            "AuthorStub",
            (),
            {
                "scopus_id": "57193901649",
                "first_name": "Lorena",
                "last_name": "Recalde",
                "auth_name": "Recalde L.",
                "initials": "L.",
                "affiliations": Related(),
                "articles": EmptyRelated(),
                "co_authors": EmptyRelated(),
                "topics": EmptyRelated(),
                "citation_count": 0,
                "current_affiliation": None,
            },
        )()

        data = AuthorSerializer(author).data

        self.assertEqual(data["current_affiliation"], "Escuela Politecnica Nacional")


class AuthorServiceSchemaTests(SimpleTestCase):
    def test_find_author_by_id_falls_back_to_article_citation_sum(self):
        inflated_author = SimpleNamespace(citation_count=0)

        with patch(
            "apps.search_engine.application.services.author_service.db.cypher_query",
            return_value=[[["author-node", 51]], ["author", "citation_count"]],
        ) as execute, patch(
            "apps.search_engine.application.services.author_service.Author.inflate",
            return_value=inflated_author,
        ):
            author = AuthorService().find_by_id("57193901649")

        query, params = execute.call_args.args
        self.assertIn("article.cited_by_count", query)
        self.assertIn(
            "coalesce(toInteger(author.citation_count), 0) > 0",
            query,
        )
        self.assertEqual(params, {"scopus_id": "57193901649"})
        self.assertEqual(author.citation_count, 51)

    def test_find_authors_by_query_uses_new_schema_and_parameters(self):
        calls = []
        inflated_author = SimpleNamespace(citation_count=0)

        def execute(query, params=None):
            calls.append((query, params))
            if "RETURN count(au)" in query:
                return [[1]], ["total"]
            return [["author-node", 51]], ["au", "citation_count"]

        with patch(
            "apps.search_engine.application.services.author_service.db.cypher_query",
            side_effect=execute,
        ), patch(
            "apps.search_engine.application.services.author_service.Author.inflate",
            return_value=inflated_author,
        ):
            authors, total = AuthorService().find_authors_by_query(
                "Jaramillo Castellón",
                page_size=10,
                page=1,
            )

        self.assertEqual(authors, [inflated_author])
        self.assertEqual(authors[0].citation_count, 51)
        self.assertEqual(total, 1)
        self.assertEqual(calls[0][1], {"name": "jaramillo castellon"})
        self.assertEqual(
            calls[1][1],
            {"name": "jaramillo castellon", "skip": 0, "page_size": 10},
        )
        for property_name in ("au.authid", "au.given_name", "au.surname", "au.authname"):
            self.assertIn(property_name, calls[0][0])
            self.assertIn(property_name, calls[1][0])
        self.assertIn("replace(", calls[0][0])
        self.assertIn("article.cited_by_count", calls[1][0])
        self.assertIn(
            "coalesce(toInteger(au.citation_count), 0) > 0",
            calls[1][0],
        )

    def test_articles_by_author_matches_authid(self):
        calls = []

        def execute(query, params=None):
            calls.append((query, params))
            return [["article-node"]], ["a"]

        with patch(
            "apps.search_engine.application.services.article_service.db.cypher_query",
            side_effect=execute,
        ), patch(
            "apps.search_engine.application.services.article_service.Article.inflate",
            side_effect=lambda node: node,
        ):
            articles = ArticleService().find_articles_by_author("58611443600")

        self.assertEqual(articles, ["article-node"])
        self.assertIn("au.authid = $author_id", calls[0][0])
        self.assertEqual(calls[0][1], {"author_id": "58611443600"})


class ArticleServiceSchemaTests(SimpleTestCase):
    @override_settings(USE_ML_MODELS_SERVICE=True)
    @patch("apps.search_engine.application.services.article_service.MLModelsClient")
    def test_relevant_articles_use_ml_microservice_when_enabled(self, ml_client_class):
        ml_client_class.return_value.search_tfidf.return_value = {
            "results": [
                {"doc_id": "A-1", "score": 0.75},
                {"doc_id": "A-2", "score": 0.50},
            ]
        }
        result = ArticleService().find_most_relevant_articles_by_topic("artificial intelligence")

        ml_client_class.return_value.search_tfidf.assert_called_once_with(
            query="artificial intelligence",
            version="v10.0",
            top_k=100,
        )
        self.assertEqual(result.index.to_list(), ["A-1", "A-2"])
        self.assertEqual(result.to_list(), [0.75, 0.50])

    def test_find_article_by_id_derives_relationship_counts(self):
        article = SimpleNamespace(author_count=None, affiliation_count=None)

        with patch(
            "apps.search_engine.application.services.article_service.db.cypher_query",
            return_value=[[["article-node", 3, 1]], ["article", "author_count", "affiliation_count"]],
        ) as execute, patch(
            "apps.search_engine.application.services.article_service.Article.inflate",
            return_value=article,
        ):
            result = ArticleService().find_by_id("105019303118")

        query, params = execute.call_args.args
        self.assertIn("count(DISTINCT author)", query)
        self.assertIn("count(DISTINCT affiliation)", query)
        self.assertEqual(params, {"article_id": "105019303118"})
        self.assertEqual(result.author_count, 3)
        self.assertEqual(result.affiliation_count, 1)

    def test_find_authors_by_article_uses_new_author_properties(self):
        with patch(
            "apps.search_engine.application.services.article_service.db.cypher_query",
            return_value=(
                [[[{"scopusId": "57192268040", "name": "Torres S.P."}]]],
                ["authors"],
            ),
        ) as execute:
            authors = ArticleService().find_authors_by_article("105019303118")

        query, params = execute.call_args.args
        self.assertIn("au.authid", query)
        self.assertIn("au.authname", query)
        self.assertEqual(params, {"article_id": "105019303118"})
        self.assertEqual(authors[0][0]["scopusId"], "57192268040")


class RelevantArticlesViewTests(SimpleTestCase):
    def test_relevance_score_is_preserved_when_articles_are_hydrated(self):
        class ArticleServiceStub:
            def find_most_relevant_articles_by_topic(self, topic):
                import pandas as pd

                return pd.Series({"A-1": 0.75}, dtype=float)

            def find_years_by_articles(self, ids):
                return ["2024-01-01"]

            def find_articles_by_ids(self, ids, page, size):
                return (
                    [
                        {
                            "scopus_id": "A-1",
                            "title": "First article",
                            "publication_date": "2024-01-01",
                            "author_count": 2,
                            "affiliation_count": 1,
                            "authors": ["Author One"],
                            "affiliations": ["University One"],
                        }
                    ],
                    1,
                )

        request = APIRequestFactory().post(
            "/most-relevant-articles-by-topic/",
            {"query": "artificial intelligence", "page": 1, "size": 10},
            format="json",
        )

        with patch.object(ArticleViewSet, "article_service", ArticleServiceStub()):
            response = ArticleViewSet.as_view(
                {"post": "most_relevant_articles_by_topic"}
            )(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"][0]["relevance"], 0.75)
