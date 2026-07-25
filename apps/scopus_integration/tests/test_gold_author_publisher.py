from django.test import SimpleTestCase


class _FakeQueryExecutor:
    def __init__(self):
        self.calls = []

    def __call__(self, query, params):
        self.calls.append((query, params))
        return [[len(params["authors"])]], ["updated"]


class Neo4jGoldAuthorPublisherTests(SimpleTestCase):
    def test_publish_deduplicates_gold_authors_and_updates_legacy_shape(self):
        try:
            from apps.scopus_integration.infrastructure.publishers.neo4j_graph_publisher import (
                Neo4jGraphPublisher,
            )
        except ImportError as error:
            self.fail(f"Neo4jGraphPublisher is required: {error}")

        executor = _FakeQueryExecutor()
        publisher = Neo4jGraphPublisher(query_executor=executor, batch_size=100)
        graph_entities = [
            {
                "authors": [
                    {
                        "author_id": "1",
                        "given_name": "Ana",
                        "surname": "Perez",
                        "indexed_name": "Perez, A.",
                        "initials": "A.",
                        "citation_count": 4,
                        "affiliation_ids": ["10"],
                    }
                ],
                "affiliations": [{"affiliation_id": "10", "name": "Universidad A"}],
            },
            {
                "authors": [
                    {
                        "author_id": "1",
                        "given_name": "Ana",
                        "surname": "Perez",
                        "indexed_name": "Perez, A.",
                        "initials": "A.",
                        "citation_count": 4,
                        "affiliation_ids": ["10"],
                    },
                    {
                        "author_id": "2",
                        "given_name": "Luis",
                        "surname": "Mora",
                        "indexed_name": "Mora, L.",
                        "initials": "L.",
                        "citation_count": 0,
                        "affiliation_ids": [],
                    },
                ],
                "affiliations": [{"affiliation_id": "10", "name": "Universidad A"}],
            },
        ]

        result = publisher.publish(graph_entities)

        self.assertEqual(result, {"authors": 2})
        self.assertEqual(len(executor.calls), 1)
        self.assertIn("authid: item.scopus_id", executor.calls[0][0])
        self.assertIn("author.given_name", executor.calls[0][0])
        self.assertIn("author.surname", executor.calls[0][0])
        self.assertIn("author.authname", executor.calls[0][0])
        authors = executor.calls[0][1]["authors"]
        self.assertEqual(
            authors,
            [
                {
                    "scopus_id": "1",
                    "first_name": "Ana",
                    "last_name": "Perez",
                    "auth_name": "Perez, A.",
                    "initials": "A.",
                    "citation_count": 4,
                    "current_affiliation": "Universidad A",
                },
                {
                    "scopus_id": "2",
                    "first_name": "Luis",
                    "last_name": "Mora",
                    "auth_name": "Mora, L.",
                    "initials": "L.",
                    "citation_count": 0,
                    "current_affiliation": "",
                },
            ],
        )
