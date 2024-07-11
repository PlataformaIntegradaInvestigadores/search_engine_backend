from urllib.parse import quote_plus as url_encode

from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.scopus_integration.application.services.model_corpus_observer_service import ModelCorpusObserverService
from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.application.usecases.search_affiliations_usecase import Search
import threading


class ScopusIntegrationViewSet(viewsets.ModelViewSet):
    model_corpus_observer = ModelCorpusObserverService()
    lock = threading.Lock()

    def list(self, request, *args, **kwargs):
        if not self.lock.acquire(blocking=False):
            return Response({"success": False, "message": "Another instance is already running."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
        try:
            search_type = "scopus"
            view = "COMPLETE"
            field = ("dc:identifier,doi,dc:title,coverDate,dc:description,authkeywords,afid,affilname,"
                     "affiliation-city,affiliation-country,authid,authname,given-name,surname,initials")
            count = "25"
            cursor = '*'
            query = url_encode("AFFIL(AFFILCOUNTRY(Ecuador))")
            url = "https://api.elsevier.com/content/search/" + search_type + "?query=" + query + "&count=" + count + "&view=" + view + "&field=" + field + "&cursor=" + cursor
            client = ScopusClient()
            article_search = Search(url=url)
            print("Iniciando la ejecucion de la busqueda .....")
            article_search.execute(client, True)
            results = article_search.results
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            self.model_corpus_observer.delete_corpus()
            self.model_corpus_observer.delete_model()
            self.lock.release()
