# -*- coding: utf-8 -*-
"""
Created on Mon May 17 2021

@author: Nicolas
updated by: Fernando
"""

from urllib.parse import quote_plus as url_encode

from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.utils.utils import encodeFacets
from apps.search_engine.application.services.article_service import ArticleService
from apps.search_engine.application.usecases.article.articles_bulk_create_usecase import ArticlesBulkCreateUseCase
from apps.search_engine.domain.entities.article import Article


class Search:
    # statics variables
    _url_base = "https://api.elsevier.com/content/search/"
    article_service = ArticleService()
    authors_bulk_create_usecase = ArticlesBulkCreateUseCase(article_service=article_service)

    def __init__(self, url=None, query=None, facets=None, view=None, field=None, searchType=None):
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

    def execute(self, client: ScopusClient = None, get_all=False):
        try:
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

                    self.results += api_response['search-results']['entry']
                    self.num_res = len(self.results)
                    print('Current results: ', self.num_res)
        except Exception as e:
            raise Exception('Error on search ' + str(e))
