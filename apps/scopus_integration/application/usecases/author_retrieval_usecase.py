from apps.scopus_integration.application.services.scopus_client import ScopusClient


class AuthorRetrieval:
    """Una author en Scopus."""

    # variables estáticas
    _url_base = u'https://api.elsevier.com/content/author/author_id/'

    def __init__(self, url=None, response_list=False, author_id=None, view=None, field=None):
        """Inicializa un author dado la URL
        del author o author ID."""
        self.result = None
        self.response_list = response_list

        if url and not author_id:
            self.url = url
        elif author_id and not url:
            self.url = self._url_base + author_id
            if view:
                self.url = self.url + '&view=' + view
            if field:
                self.url = self.url + '&field=' + field
        elif not url and not author_id:
            raise ValueError('No se ha especificado ningún URL e ID.')
        else:
            raise ValueError(
                'Se ha especificado tanto el URL como el ID. Solo se necesita uno.')

    def execute(self, client: ScopusClient = None):
        api_response = client.exec_request(self.url)
        if self.response_list:
            self.result = api_response['author-retrieval-response-list']['author-retrieval-response']
        else:
            self.result = api_response['author-retrieval-response']
        # TODO filtrar respuesta
