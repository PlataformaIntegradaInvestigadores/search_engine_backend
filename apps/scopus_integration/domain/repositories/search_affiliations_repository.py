# -*- coding: utf-8 -*-
"""
Created on Mon May 17 2021

@author: Nicolas
updated by: Fernando
"""

from urllib.parse import quote_plus as url_encode

import requests
import logging

from neomodel import db

from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.domain.entities.cursor_reference import CursorReference
from apps.scopus_integration.utils.utils import encodeFacets
from apps.search_engine.application.services.article_service import ArticleService
from apps.search_engine.domain.entities.article import Article

logger = logging.getLogger('django')


class SearchAffiliationRepository:
    # statics variables
    _url_base = "https://api.elsevier.com/content/search/"
    article_service = ArticleService()

    def __init__(self, url, query=None, facets=None, view=None, field=None, searchType=None):
        self.num_res = None
        self.tot_num_res = None
        self.results = None
        self.facets = facets
        if url and not query:
            self.url = url
        elif query and not url:
            if not searchType:
                raise ValueError('Type of search is needed.')
            self.url = self._url_base + searchType + '?query=' + url_encode(query)
            if view:
                self.url = self.url + '&view=' + view
            if field:
                self.url = self.url + '&field=' + field
            if facets:
                self.url = self.url + '&facets=' + facets
        elif not url and not query:
            raise ValueError('URL or query is needed.')
        else:
            raise ValueError(
                'Just one parameter is needed, either the URL or the query. Not both.')

    def retrieve(self, client: ScopusClient = None, get_all=False):
        try:
            next_url = ""
            api_response = client.exec_request(self.url)

            if 'search-results' not in api_response:
                raise ValueError("Invalid API response: missing 'search-results'")

            self.tot_num_res = int(api_response['search-results'].get('opensearch:totalResults', 0))
            logger.info(f"Total results: {self.tot_num_res}")

            self.results = api_response['search-results'].get('entry', [])
            self.num_res = len(self.results)
            logger.info(f'Current results: {self.num_res}')

            existing_cursors = {cursor.next_url for cursor in CursorReference.nodes.all()}
            logger.info(f"Existing cursors: {existing_cursors}")

            if get_all is True:
                while self.num_res < self.tot_num_res:
                    with db.transaction:
                        next_url = None
                        for e in api_response['search-results'].get('link', []):
                            if e.get('@ref') == 'next':
                                next_url = e.get('@href')
                                if next_url in existing_cursors:
                                    logger.info(f"Cursor {next_url} already exists. Skipping...")
                                    break
                                else:
                                    logger.info(f"Creating cursor {next_url}")
                                    CursorReference(next_url=encodeFacets(next_url, facets=self.facets)).save()

                        if not next_url:
                            logger.info("No next URL found, stopping.")
                            break

                        api_response = client.exec_request(encodeFacets(next_url, self.facets))
                        new_entries = api_response['search-results'].get('entry', [])

                        for article_ in new_entries:
                            try:
                                scopus_id = Article.validate_scopus_id(article_.get('dc:identifier', ''))
                                doi = article_.get('prism:doi', '') or None
                            except ValueError as e:
                                logger.error(f"Error on article validation: {e}")
                                continue
                            else:
                                logger.info(f"Creating article with Scopus ID {scopus_id}")
                                Article.from_json(article_, client)

                        self.results += new_entries
                        self.num_res = len(self.results)

        except requests.HTTPError as e:
            logger.error(f"Error on search due to HTTP error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise
