from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.scopus_integration.application.services.model_corpus_observer_service import ModelCorpusObserverService
from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.application.usecases.update_author_information_usecase import \
    UpdateAuthorInformationUseCase
from apps.search_engine.application.services.author_service import AuthorService
import threading


class UpdateInformationViewSet(viewsets.ViewSet):
    client = ScopusClient()
    author_repository = AuthorService()
    model_corpus_observer = ModelCorpusObserverService()
    lock = threading.Lock()

    @action(detail=False, methods=['post'], url_path='author-information', url_name='update-author-information')
    def update_author_information(self, request, *args, **kwargs):
        if not self.lock.acquire(blocking=False):
            return Response({'success': False, 'message': 'Another instance is already running.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
        try:
            update_author_information_usecase = UpdateAuthorInformationUseCase(author_repository=self.author_repository,
                                                                               client=self.client)
            total = update_author_information_usecase.execute()
            return Response({'success': True, 'message': total + "authors was update successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            self.model_corpus_observer.delete_corpus()
            self.model_corpus_observer.delete_model()
            self.lock.release()