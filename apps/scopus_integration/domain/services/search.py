# -*- coding: utf-8 -*-
"""
Created on Mon May 17 2021

@author: Nicolas
"""

from urllib.parse import quote_plus as url_encode

from django.db import transaction
from neomodel import db

from apps.scopus_integration.domain.services.scopus_client import ScopusClient
from apps.scopus_integration.utils.utils import encodeFacets
from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.entities.topic import Topic


class Search:
    # statics variables
    _url_base = "https://api.elsevier.com/content/search/"

    def __init__(self, url=None, query=None, facets=None, view=None, field=None, searchType=None):
        self.num_res = None
        self.tot_num_res = None
        self.results = None
        self.facets = facets
        if url and not query:
            self.url = url
        elif query and not url:
            if not searchType:
                raise ValueError('No se ha especificado el tipo de búsqueda.')
            self.url = self._url_base + searchType + '?query=' + url_encode(query)
            if view:
                self.url = self.url + '&view=' + view
            if field:
                self.url = self.url + '&field=' + field
            if facets:
                self.url = self.url + '&facets=' + facets
        elif not url and not query:
            raise ValueError('No se ha especificado ningún URL o query.')
        else:
            raise ValueError(
                'Se ha especificado tanto el URL como la query. Solo se necesita uno.')

    def execute(self, client: ScopusClient = None, get_all=False):
        next_url = ""
        api_response = client.exec_request(self.url)
        self.tot_num_res = int(api_response['search-results']['opensearch:totalResults'])
        print("Total results:", self.tot_num_res)
        self.results = api_response['search-results']['entry']
        self.num_res = len(self.results)
        print('Current results: ', self.num_res)
        if get_all is True:
            while self.num_res < self.tot_num_res:
                for e in api_response['search-results']['link']:
                    if e['@ref'] == 'next':
                        next_url = e['@href']
                api_response = client.exec_request(encodeFacets(next_url, self.facets))

                # Create new Articles extracted directly from the API response
                articles = []
                for article_ in api_response['search-results']['entry']:
                    article_data = Article.from_json(article_)
                    articles.append(article_data)

                with transaction.atomic():
                    Article.create_or_update(*articles)

                self.results += api_response['search-results']['entry']

                self.num_res = len(self.results)
                print('Current results: ', self.num_res)
