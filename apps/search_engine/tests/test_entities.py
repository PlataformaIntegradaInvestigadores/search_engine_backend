"""
Unit tests for domain entities (Neo4j DjangoNode classes).

Tests cover:
- Topic: clean_topic() method and from_json() factory
- Author: node creation with required fields, EXPERT_IN relationship to Topic
- Article: node creation with fields
- Affiliation: uniqueness constraint behavior (name unique_index)

These tests run against a real Neo4j instance configured in CI.
"""
from neomodel import DoesNotExist
from rest_framework.test import APITestCase

from apps.search_engine.domain.entities.topic import Topic
from apps.search_engine.domain.entities.author import Author
from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.entities.affiliation import Affiliation


class TopicCleanTests(APITestCase):
    """Tests for Topic.clean_topic() static method (no DB required)."""

    def test_clean_topic_converts_to_lowercase(self):
        result = Topic.clean_topic("Machine Learning")
        self.assertEqual(result, "machine learning")

    def test_clean_topic_removes_special_characters(self):
        result = Topic.clean_topic("data-science & AI!")
        self.assertEqual(result, "datascience  ai")

    def test_clean_topic_removes_accents_via_unidecode(self):
        result = Topic.clean_topic("Inteligencia Artificial")
        self.assertEqual(result, "inteligencia artificial")

    def test_clean_topic_handles_unicode_characters(self):
        result = Topic.clean_topic("Redes Neuronales")
        self.assertEqual(result, "redes neuronales")

    def test_clean_topic_strips_whitespace(self):
        result = Topic.clean_topic("  deep learning  ")
        self.assertEqual(result, "deep learning")

    def test_clean_topic_removes_parentheses_and_brackets(self):
        result = Topic.clean_topic("NLP (Natural Language Processing)")
        self.assertEqual(result, "nlp natural language processing")

    def test_clean_topic_preserves_numbers(self):
        result = Topic.clean_topic("Web 3.0 Technologies")
        self.assertEqual(result, "web 30 technologies")


class TopicFromJsonTests(APITestCase):
    """Tests for Topic.from_json() factory (requires Neo4j)."""

    def test_from_json_creates_new_topic(self):
        topic = Topic.from_json("Graph Databases")
        self.assertIsNotNone(topic)
        self.assertEqual(topic.name, "graph databases")
        # Cleanup
        topic.delete()

    def test_from_json_returns_existing_topic_if_duplicate(self):
        topic1 = Topic.from_json("Neural Networks")
        topic2 = Topic.from_json("Neural Networks")
        self.assertEqual(topic1.element_id, topic2.element_id)
        # Cleanup
        topic1.delete()

    def test_from_json_cleans_topic_before_saving(self):
        topic = Topic.from_json("DATA SCIENCE!")
        self.assertEqual(topic.name, "data science")
        # Cleanup
        topic.delete()

    def test_from_json_deduplicates_after_cleaning(self):
        """Two inputs that differ only in casing/special chars map to the same node."""
        topic1 = Topic.from_json("Deep-Learning")
        topic2 = Topic.from_json("deep learning")
        self.assertEqual(topic1.element_id, topic2.element_id)
        # Cleanup
        topic1.delete()


class AuthorNodeTests(APITestCase):
    """Tests for Author node creation and relationships."""

    def test_create_author_with_required_fields(self):
        author = Author(
            scopus_id="12345678",
            first_name="John",
            last_name="Doe",
            auth_name="Doe J.",
            initials="J.",
        ).save()
        self.assertIsNotNone(author)
        self.assertEqual(author.first_name, "John")
        self.assertEqual(author.last_name, "Doe")
        self.assertEqual(author.scopus_id, "12345678")
        # Cleanup
        author.delete()

    def test_author_default_citation_count(self):
        author = Author(
            scopus_id="99999999",
            first_name="Jane",
            last_name="Smith",
            auth_name="Smith J.",
            initials="J.",
        ).save()
        self.assertEqual(author.citation_count, 0)
        # Cleanup
        author.delete()

    def test_author_str_representation(self):
        author = Author(
            scopus_id="11111111",
            first_name="Albert",
            last_name="Einstein",
            auth_name="Einstein A.",
            initials="A.",
        ).save()
        self.assertEqual(str(author), "Albert Einstein")
        # Cleanup
        author.delete()

    def test_author_from_dict_creates_node(self):
        data = {
            "authid": "55555555",
            "given-name": "Marie",
            "surname": "Curie",
            "initials": "M.",
            "authname": "Curie M.",
        }
        author = Author.from_dict(data)
        self.assertIsNotNone(author)
        self.assertEqual(author.first_name, "Marie")
        self.assertEqual(author.last_name, "Curie")
        # Cleanup
        author.delete()

    def test_author_from_dict_raises_on_empty_scopus_id(self):
        data = {
            "authid": "",
            "given-name": "No",
            "surname": "Id",
        }
        with self.assertRaises(ValueError):
            Author.from_dict(data)

    def test_author_expert_in_relationship_to_topic(self):
        """Test that an Author can be connected to a Topic via EXPERT_IN."""
        author = Author(
            scopus_id="77777777",
            first_name="Ada",
            last_name="Lovelace",
            auth_name="Lovelace A.",
            initials="A.",
        ).save()
        topic = Topic.from_json("Computer Science")

        # Connect relationship
        author.topics.connect(topic)
        self.assertTrue(author.topics.is_connected(topic))

        # Verify we can retrieve the connected topic
        connected_topics = author.topics.all()
        self.assertEqual(len(connected_topics), 1)
        self.assertEqual(connected_topics[0].name, "computer science")

        # Cleanup
        author.topics.disconnect(topic)
        author.delete()
        topic.delete()


class ArticleNodeTests(APITestCase):
    """Tests for Article node creation."""

    def test_create_article_with_fields(self):
        article = Article(
            scopus_id="ART001",
            title="A Study on Graph Databases",
            abstract="This paper explores graph databases.",
            doi="10.1234/test.001",
            publication_date="2024-01-15",
            author_count=3,
            affiliation_count=2,
        ).save()
        self.assertIsNotNone(article)
        self.assertEqual(article.title, "A Study on Graph Databases")
        self.assertEqual(article.scopus_id, "ART001")
        self.assertEqual(article.author_count, 3)
        # Cleanup
        article.delete()

    def test_article_str_representation(self):
        article = Article(
            scopus_id="ART002",
            title="Deep Learning for NLP",
            abstract="Abstract text here.",
            publication_date="2023-06-01",
        ).save()
        self.assertEqual(str(article), "Deep Learning for NLP")
        # Cleanup
        article.delete()

    def test_article_validate_scopus_id_valid(self):
        result = Article.validate_scopus_id("SCOPUS_ID:123456")
        self.assertEqual(result, "123456")

    def test_article_validate_scopus_id_empty(self):
        result = Article.validate_scopus_id("")
        self.assertIsNone(result)

    def test_article_validate_scopus_id_none(self):
        result = Article.validate_scopus_id(None)
        self.assertIsNone(result)

    def test_article_topic_relationship(self):
        """Test USES relationship between Article and Topic."""
        article = Article(
            scopus_id="ART003",
            title="Knowledge Graphs",
            abstract="Exploring knowledge graphs.",
            publication_date="2024-03-01",
        ).save()
        topic = Topic.from_json("Knowledge Representation")

        article.topics.connect(topic)
        self.assertTrue(article.topics.is_connected(topic))

        # Cleanup
        article.topics.disconnect(topic)
        article.delete()
        topic.delete()

    def test_calculate_collab_strength(self):
        """Test the static method for collaboration strength calculation."""
        # collab_strength = shared_pubs / sqrt(total_a * total_b)
        result = Article.calculate_collab_strength(2, 4, 4)
        self.assertAlmostEqual(result, 0.5)

        result = Article.calculate_collab_strength(1, 1, 1)
        self.assertAlmostEqual(result, 1.0)


class AffiliationNodeTests(APITestCase):
    """Tests for Affiliation node creation and uniqueness."""

    def test_create_affiliation(self):
        affiliation = Affiliation(
            scopus_id="AFF001",
            name="Escuela Politecnica Nacional",
            city="Quito",
            country="Ecuador",
        ).save()
        self.assertIsNotNone(affiliation)
        self.assertEqual(affiliation.name, "Escuela Politecnica Nacional")
        self.assertEqual(affiliation.country, "Ecuador")
        # Cleanup
        affiliation.delete()

    def test_affiliation_from_dict(self):
        data = {
            "afid": "AFF002",
            "affilname": "MIT",
            "affiliation-city": "Cambridge",
            "affiliation-country": "United States",
        }
        affiliation = Affiliation.from_dict(data)
        self.assertIsNotNone(affiliation)
        self.assertEqual(affiliation.name, "MIT")
        self.assertEqual(affiliation.city, "Cambridge")
        # Cleanup
        affiliation.delete()

    def test_affiliation_from_dict_returns_existing_by_scopus_id(self):
        """If an affiliation with the same scopus_id exists, return it."""
        data = {
            "afid": "AFF003",
            "affilname": "Stanford University",
            "affiliation-city": "Stanford",
            "affiliation-country": "United States",
        }
        aff1 = Affiliation.from_dict(data)
        aff2 = Affiliation.from_dict(data)
        self.assertEqual(aff1.element_id, aff2.element_id)
        # Cleanup
        aff1.delete()

    def test_affiliation_from_dict_returns_existing_by_name(self):
        """If scopus_id doesn't match but name does, update and return existing."""
        aff_original = Affiliation(
            scopus_id="AFF_OLD",
            name="Harvard University",
            city="Cambridge",
            country="United States",
        ).save()

        data = {
            "afid": "AFF_NEW",
            "affilname": "Harvard University",
            "affiliation-city": "Cambridge",
            "affiliation-country": "United States",
        }
        aff_found = Affiliation.from_dict(data)
        # Should return the same node (matched by name)
        self.assertEqual(aff_found.element_id, aff_original.element_id)
        # The scopus_id should be updated
        aff_found.refresh()
        self.assertEqual(aff_found.scopus_id, "AFF_NEW")
        # Cleanup
        aff_found.delete()

    def test_affiliation_article_relationship(self):
        """Test BELONGS_TO relationship between Article and Affiliation."""
        article = Article(
            scopus_id="ART_AFF_TEST",
            title="Test Article",
            abstract="Testing affiliations.",
            publication_date="2024-01-01",
        ).save()
        affiliation = Affiliation(
            scopus_id="AFF_REL",
            name="University of Test",
            city="Test City",
            country="Testland",
        ).save()

        article.affiliations.connect(affiliation)
        self.assertTrue(article.affiliations.is_connected(affiliation))

        # Cleanup
        article.affiliations.disconnect(affiliation)
        article.delete()
        affiliation.delete()
