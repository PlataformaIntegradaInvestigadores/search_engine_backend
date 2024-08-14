"""
@author: Nicolas
updated by: Fernando
"""

from urllib.parse import quote_plus as url_encode

import requests
import logging
from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.utils.utils import encodeFacets
from apps.search_engine.application.services.article_service import ArticleService
from apps.search_engine.application.usecases.article.articles_bulk_create_usecase import ArticlesBulkCreateUseCase
from apps.search_engine.domain.entities.article import Article

logger = logging.getLogger('django')


class Search:
    # statics variables
    _url_base = "https://api.elsevier.com/content/search/"
    article_service = ArticleService()

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
            logger.log(logging.INFO, f"Total results: {self.tot_num_res}")
            self.results = api_response['search-results']['entry']
            self.num_res = len(self.results)
            print('Current results: ', self.num_res)
            logger.log(logging.INFO, f'Current results: {self.num_res}')
            existing_articles = {article.scopus_id for article in
                                 Article.nodes.all()}
            if get_all is True:
                while self.num_res < self.tot_num_res:
                    for e in api_response['search-results']['link']:
                        if e['@ref'] == 'next':
                            next_url = e['@href']
                    api_response = client.exec_request(encodeFacets(next_url, self.facets))
                    # Create new Articles extracted directly from the API response
                    articles = []
                    for article_ in api_response['search-results']['entry']:
                        try:
                            scopus_id = Article.validate_scopus_id(article_.get('dc:identifier', ''))
                            doi = article_.get('prism:doi', '') if article_.get('prism:doi', '') else None
                        except ValueError as e:
                            print("Error on article validation: ", e)
                            logger.log(logging.ERROR, f"Error on article validation: {e}")
                            continue

                            # Check if the article already exists in the database
                        if scopus_id in existing_articles:
                            logger.log(logging.INFO, f"Article with Scopus ID {scopus_id} already exists.")
                            print(f"Article with Scopus ID {scopus_id} already exists.")
                        else:
                            print(f"Creating article with Scopus ID {scopus_id}")
                            print(f"DOI: {doi}")
                            logger.log(logging.INFO, f"Creating article with Scopus ID {scopus_id}")
                            Article.from_json(article_, client)

                        existing_articles.add(scopus_id)  # Update the set with the new article's Scopus I

                    self.results += api_response['search-results']['entry']
                    self.num_res = len(self.results)
                    logger.log(logging.INFO, f"Current updates {self.num_res}")
                    print('Current results: ', self.num_res)
        except requests.HTTPError as e:
            raise e
        except Exception as e:
            raise Exception('Error on search ' + str(e))
