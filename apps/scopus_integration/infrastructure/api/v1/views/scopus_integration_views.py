from urllib.parse import quote_plus as url_encode

from rest_framework import viewsets
from rest_framework.response import Response

from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.application.services.search import Search


class ScopusIntegrationViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        try:
            search_type = "scopus"
            view = "COMPLETE"
            field = ("dc:identifier,doi,dc:title,coverDate,dc:description,authkeywords,afid,affilname,"
                     "affiliation-city,affiliation-country,authid,authname,given-name,surname,initials")
            count = "25"
            cursor = '*'
            query = url_encode("AFFIL(AFFILCOUNTRY(Ecuador))")
            url = "https://api.elsevier.com/content/search/" + search_type + "?query=" + query + "&count=" + count + "&view=" + view + "&field=" + field + "&cursor=" + cursor
            print("url:", url)
            client = ScopusClient()
            article_search = Search(url=url)
            print("Iniciando la ejecucion de la busqueda .....")
            article_search.execute(client, True)
            results = article_search.results
            return Response({"message": "Hello, world!", "results": results})
        except Exception as e:
            return Response({"message": "Error: " + str(e)})
