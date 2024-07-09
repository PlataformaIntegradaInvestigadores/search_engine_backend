from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.scopus_integration.application.services.model_corpus_observer_service import ModelCorpusObserverService
from apps.scopus_integration.application.services.search_scopus_service import RetrieveScopusData
from apps.search_engine.application.services.article_service import ArticleService
from apps.search_engine.application.services.author_service import AuthorService


class DashboardInformationViewSet(viewsets.ViewSet):
    author_service = AuthorService()
    article_service = ArticleService()
    retrieve_scopus_data = RetrieveScopusData()
    model_corpus_observer = ModelCorpusObserverService()

    @extend_schema(
        summary='Get the total number of authors',
        description='This endpoint returns the total number of authors in the system.',
        tags=['Dashboard Information']
    )
    @action(detail=False, methods=['get'], url_path='get_authors_comparator')
    def get_authors_comparator(self, request, *args, **kwargs):
        try:
            authors_no_updated = self.author_service.get_authors_no_updated_count()
            total_authors = self.author_service.authors_count()
            return Response({'authors_no_updated': authors_no_updated, 'total_authors': total_authors},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Get the total number of articles',
        description='This endpoint returns the total number of articles in the system.',
        tags=['Dashboard Information']
    )
    @action(detail=False, methods=['get'], url_path='get_articles_comparator')
    def get_articles_comparator(self, request, *args, **kwargs):
        try:
            total_articles_centinela = self.article_service.articles_count()
            total_articles_scopus = self.retrieve_scopus_data.get_total_articles_from_scopus()
            return Response({'total_centinela': total_articles_centinela,
                             'total_scopus': int(total_articles_scopus)},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Verify if model and corpus paths exist',
        description='This endpoint returns if the model and corpus paths exist.',
        tags=['Dashboard Information']
    )
    @action(detail=False, methods=['get'], url_path='tfidf_model_corpus')
    def tfidf_model_corpus(self, request):
        try:
            model_exists = self.model_corpus_observer.verify_model_path_exists()
            corpus_exists = self.model_corpus_observer.verify_corpus_path_exists()
            return Response({'model': model_exists, 'corpus': corpus_exists}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
