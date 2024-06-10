from apps.scopus_integration.domain.services.scopus_client import ScopusClient


class ArticleRetrieval():
    """Un Article en Scopus."""

    # variables estáticas
    _url_base = u'https://api.elsevier.com/content/abstract/scopus_id/'

    def __init__(self, url=None, scopus_id=None, view=None, field=None):
        """Inicializa un article dado la URL
        del article o Scopus ID."""

        self.result = None
        if url and not scopus_id:
            self.url = url
        elif scopus_id and not url:
            self.url = self._url_base + scopus_id
            if view:
                self.url = self.url + '&view=' + view
            if field:
                self.url = self.url + '&field=' + field
        elif not url and not scopus_id:
            raise ValueError('No se ha especificado ningún URL e ID.')
        else:
            raise ValueError(
                'Se ha especificado tanto el URL como el ID. Solo se necesita uno.')

    def execute(self, client: ScopusClient = None):
        api_response = client.exec_request(self.url)
        self.result = api_response['abstracts-retrieval-response']
