import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.search_engine.domain.entities.topic import Topic
from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.entities.affiliation import Affiliation


@pytest.mark.integration
class TopicAPIIntegrationTest(APITestCase):
    """Integration: Topic API endpoint → ViewSet → Service → Neo4j."""

    def setUp(self):
        self.client = APIClient()
        self.topic1 = Topic.from_json("Artificial Intelligence")
        self.topic2 = Topic.from_json("Machine Learning")

    def tearDown(self):
        try:
            self.topic1.delete()
        except Exception:
            pass
        try:
            self.topic2.delete()
        except Exception:
            pass

    def test_list_topics_returns_200(self):
        response = self.client.get("/api-se/v1/topics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_topics_contains_created_topics(self):
        response = self.client.get("/api-se/v1/topics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        topic_names = [t["name"] for t in response.data]
        self.assertIn("artificial intelligence", topic_names)
        self.assertIn("machine learning", topic_names)

    def test_list_topics_response_is_list(self):
        response = self.client.get("/api-se/v1/topics/")
        self.assertIsInstance(response.data, list)

    def test_topics_have_name_field(self):
        response = self.client.get("/api-se/v1/topics/")
        for topic in response.data:
            self.assertIn("name", topic)


@pytest.mark.integration
class AuthorAPIIntegrationTest(APITestCase):
    """Integration: Author API endpoint → ViewSet → Service → Neo4j."""

    def setUp(self):
        self.client = APIClient()
        self.author = Author(
            scopus_id="INT_TEST_001",
            first_name="Integration",
            last_name="Test",
            auth_name="Test I.",
            initials="I.",
            h_index=15,
            citation_count=500,
        ).save()
        self.topic = Topic.from_json("Integration Testing")
        self.author.topics.connect(self.topic)

    def tearDown(self):
        try:
            self.author.topics.disconnect(self.topic)
        except Exception:
            pass
        try:
            self.author.delete()
        except Exception:
            pass
        try:
            self.topic.delete()
        except Exception:
            pass

    def test_list_authors_returns_200(self):
        response = self.client.get("/api-se/v1/authors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_authors_returns_paginated_response(self):
        response = self.client.get("/api-se/v1/authors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.integration
class ArticleAPIIntegrationTest(APITestCase):
    """Integration: Article creation and relationship queries via Neo4j."""

    def setUp(self):
        self.author = Author(
            scopus_id="ART_INT_001",
            first_name="Article",
            last_name="Author",
            auth_name="Author A.",
            initials="A.",
        ).save()
        self.article = Article(
            scopus_id="ARTICLE_INT_001",
            title="Integration Test Article",
            abstract="Testing article creation flow.",
            publication_date="2024-06-15",
            author_count=1,
        ).save()
        self.topic = Topic.from_json("Software Testing")
        self.article.topics.connect(self.topic)
        self.article.authors.connect(self.author)

    def tearDown(self):
        try:
            self.article.topics.disconnect(self.topic)
        except Exception:
            pass
        try:
            self.article.authors.disconnect(self.author)
        except Exception:
            pass
        try:
            self.article.delete()
        except Exception:
            pass
        try:
            self.author.delete()
        except Exception:
            pass
        try:
            self.topic.delete()
        except Exception:
            pass

    def test_article_connected_to_author(self):
        self.assertTrue(self.article.authors.is_connected(self.author))

    def test_article_connected_to_topic(self):
        self.assertTrue(self.article.topics.is_connected(self.topic))

    def test_author_articles_relationship(self):
        articles = self.author.articles.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Integration Test Article")

    def test_topic_accessible_from_article(self):
        topics = self.article.topics.all()
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0].name, "software testing")


@pytest.mark.integration
class CrossEntityIntegrationTest(APITestCase):
    """Integration: Tests the full graph structure (Author → Article → Topic → Affiliation)."""

    def setUp(self):
        self.affiliation = Affiliation(
            scopus_id="CROSS_AFF_001",
            name="Test University",
            city="Quito",
            country="Ecuador",
        ).save()
        self.author = Author(
            scopus_id="CROSS_AUTH_001",
            first_name="Cross",
            last_name="Entity",
            auth_name="Entity C.",
            initials="C.",
        ).save()
        self.article = Article(
            scopus_id="CROSS_ART_001",
            title="Cross Entity Integration",
            abstract="Full graph test.",
            publication_date="2024-01-01",
            author_count=1,
            affiliation_count=1,
        ).save()
        self.topic = Topic.from_json("Graph Integration")

        self.article.authors.connect(self.author)
        self.article.topics.connect(self.topic)
        self.article.affiliations.connect(self.affiliation)
        self.author.topics.connect(self.topic)

    def tearDown(self):
        try:
            self.article.authors.disconnect(self.author)
            self.article.topics.disconnect(self.topic)
            self.article.affiliations.disconnect(self.affiliation)
            self.author.topics.disconnect(self.topic)
        except Exception:
            pass
        try:
            self.article.delete()
        except Exception:
            pass
        try:
            self.author.delete()
        except Exception:
            pass
        try:
            self.topic.delete()
        except Exception:
            pass
        try:
            self.affiliation.delete()
        except Exception:
            pass

    def test_full_graph_traversal_author_to_affiliation(self):
        articles = self.author.articles.all()
        self.assertEqual(len(articles), 1)
        affiliations = articles[0].affiliations.all()
        self.assertEqual(len(affiliations), 1)
        self.assertEqual(affiliations[0].name, "Test University")

    def test_full_graph_traversal_topic_to_author(self):
        author_topics = self.author.topics.all()
        topic_names = [t.name for t in author_topics]
        self.assertIn("graph integration", topic_names)

    def test_affiliation_country(self):
        affs = self.article.affiliations.all()
        self.assertEqual(affs[0].country, "Ecuador")
