import threading
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from apps.dashboards.application.services.populate_service import PopulateService
from apps.dashboards.infrastructure.api.v1.views.populate_view import PopulateView
from apps.dashboards.utils.utils import process_affiliation_name


class PopulateViewTests(SimpleTestCase):
    def test_post_accepts_population_without_running_it_in_request_thread(self):
        request_thread_id = threading.get_ident()
        population_thread_id = None
        population_called = threading.Event()

        class RecordingPopulateService:
            def populate(self):
                nonlocal population_thread_id
                population_thread_id = threading.get_ident()
                population_called.set()

        request = APIRequestFactory().post('/api-se/v1/dashboard/populate', {})

        with patch.object(PopulateView, 'populate_service', RecordingPopulateService()):
            response = PopulateView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data,
            {
                'success': True,
                'message': 'Analytics DB population started',
            },
        )
        self.assertTrue(population_called.wait(timeout=1))
        self.assertNotEqual(population_thread_id, request_thread_id)
        self.assertTrue(PopulateView.lock.acquire(timeout=1))
        PopulateView.lock.release()

    def test_post_rejects_a_second_population_while_one_is_running(self):
        population_started = threading.Event()
        release_population = threading.Event()
        population_finished = threading.Event()

        class BlockingPopulateService:
            def populate(self):
                population_started.set()
                release_population.wait(timeout=2)
                population_finished.set()

        request_factory = APIRequestFactory()

        try:
            with patch.object(PopulateView, 'populate_service', BlockingPopulateService()):
                first_response = PopulateView.as_view()(
                    request_factory.post('/api-se/v1/dashboard/populate', {})
                )
                self.assertTrue(population_started.wait(timeout=1))
                second_response = PopulateView.as_view()(
                    request_factory.post('/api-se/v1/dashboard/populate', {})
                )

            self.assertEqual(first_response.status_code, status.HTTP_202_ACCEPTED)
            self.assertEqual(second_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        finally:
            release_population.set()
            self.assertTrue(population_finished.wait(timeout=1))


class PopulateServiceNeo4jSchemaTests(SimpleTestCase):
    @patch('apps.dashboards.application.services.populate_service.db.cypher_query')
    def test_author_aggregation_reads_authid_from_neo4j(self, cypher_query):
        cypher_query.return_value = (
            [['123', '456', '2020-01-01', 'Artificial intelligence']],
            [],
        )

        authors = PopulateService().get_authors_dict()

        query = cypher_query.call_args.args[0]
        self.assertIn('RETURN au.authid, ar.scopus_id', query)
        self.assertNotIn('au.scopus_id', query)
        self.assertEqual(authors[0]['scopus_id'], '123')

    @patch('apps.dashboards.application.services.populate_service.db.cypher_query')
    def test_affiliation_aggregations_read_afid_from_neo4j(self, cypher_query):
        service = PopulateService()
        cases = (
            (
                service.get_provinces_dict,
                [['6001', 'Universidad de Cuenca', 'Cuenca', '456', '2020-01-01', 'AI']],
            ),
            (
                service.get_country_affiliations_dict,
                [['6001', 'Universidad de Cuenca', '456', '2020-01-01', 'AI']],
            ),
            (
                service.get_affiliations_dict,
                [['6001', 'Universidad de Cuenca', '456', '2020-01-01', 'AI']],
            ),
        )

        for aggregation, rows in cases:
            with self.subTest(aggregation=aggregation.__name__):
                cypher_query.return_value = (rows, [])
                aggregation()
                query = cypher_query.call_args.args[0]
                self.assertIn('RETURN af.afid, af.name', query)
                self.assertNotIn('af.scopus_id', query)

    @patch('apps.dashboards.application.services.populate_service.db.cypher_query')
    def test_province_aggregation_does_not_expand_articles_by_topic(self, cypher_query):
        cypher_query.return_value = (
            [
                ['6001', 'Universidad de Cuenca', 'Cuenca', 'A-1', '2020-01-01'],
                ['6002', 'Otra afiliacion', 'Cuenca', 'A-1', '2020-01-01'],
                ['6003', 'Universidad Nacional de Loja', 'Loja', 'A-2', '2021-02-02'],
            ],
            [],
        )

        provinces = PopulateService().get_provinces_dict()

        query = cypher_query.call_args.args[0]
        self.assertNotIn('USES', query)
        self.assertNotIn('t.name', query)
        azuay = next(province for province in provinces if province['province_name'] == 'AZUAY')
        loja = next(province for province in provinces if province['province_name'] == 'LOJA')
        self.assertEqual(azuay['total_articles'], 1)
        self.assertEqual(loja['total_articles'], 1)
        self.assertEqual(azuay['topics'], [])

    @patch('apps.dashboards.utils.utils.find_province')
    def test_province_location_is_resolved_once_per_distinct_city(self, find_province):
        find_province.side_effect = [('01', 'AZUAY'), ('11', 'LOJA')]

        process_affiliation_name(
            ['Cuenca', 'Cuenca', 'Loja'],
            ['A-1', 'A-2', 'A-3'],
            ['2020', '2021', '2022'],
            [' ', ' ', ' '],
        )

        self.assertEqual(find_province.call_count, 2)
