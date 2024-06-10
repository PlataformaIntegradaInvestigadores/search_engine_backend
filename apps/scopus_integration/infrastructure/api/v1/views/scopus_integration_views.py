from urllib.parse import quote_plus as url_encode

from rest_framework import viewsets
from rest_framework.response import Response

from apps.scopus_integration.domain.services.scopus_client import ScopusClient
from apps.scopus_integration.domain.services.search import Search


class ScopusIntegrationViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        try:
            # Tipo de búsqueda
            searchType = "scopus"
            # Lista de elementos que se devolverán en la respuesta
            view = "COMPLETE"
            # Nombre de campos específicos que deben retornarse
            field = "dc:identifier,doi,dc:title,coverDate,dc:description,authkeywords,afid,affilname,affiliation-city,affiliation-country,authid,authname,given-name,surname,initials"
            # Número máximo de resultados que se devolverán por petición
            count = "25"
            # Parámetro se utiliza para ejecutar una búsqueda de paginación profunda
            cursor = '*'
            # Búsqueda booleana que se ejecutará en el clúster de SCOPUS.
            query = url_encode("AFFIL(AFFILCOUNTRY(Ecuador))")
            # Url de búsqueda de artículos
            url = "https://api.elsevier.com/content/search/" + searchType + "?query=" + query + "&count=" + count + "&view=" + view + "&field=" + field + "&cursor=" + cursor
            print("url:", url)
            client = ScopusClient()
            articleSearch = Search(url=url)
            print("Iniciando la ejecucion de la busqueda .....")
            articleSearch.execute(client, True)
            results = articleSearch.results
            return Response({"message": "Hello, world!", "results": results})
        except Exception as e:
            return Response({"message": "Error: " + str(e)})