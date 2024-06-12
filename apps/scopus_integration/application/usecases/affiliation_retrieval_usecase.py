from apps.scopus_integration.application.services.scopus_client import ScopusClient


class AffilRetrieval:
    """Una affilliation en Scopus."""

    # variables estáticas
    _url_base = u'https://api.elsevier.com/content/affiliation/affiliation_id/'

    def __init__(self, url=None, affil_id=None, view=None, field=None):
        """Inicializa una affiliation dado la URL 
        de la affiliation o affiliation ID."""

        self.result = None
        if url and not affil_id:
            self.url = url
        elif affil_id and not url:
            self.url = self._url_base + affil_id
            if view:
                self.url = self.url + '&view=' + view
            if field:
                self.url = self.url + '&field=' + field
        elif not url and not affil_id:
            raise ValueError('No se ha especificado ningún URL e ID.')
        else:
            raise ValueError(
                'Se ha especificado tanto el URL como el ID. Solo se necesita uno.')

    def execute(self, client: ScopusClient = None):
        api_response = client.exec_request(self.url)
        self.result = api_response['affiliation-retrieval-response']
