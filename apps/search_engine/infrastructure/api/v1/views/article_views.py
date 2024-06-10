from drf_spectacular.utils import extend_schema
from neomodel import clear_neo4j_database, db
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets

from apps.search_engine.domain.entities.article import Article
from apps.search_engine.domain.services.article_service import ArticleService
from apps.search_engine.infrastructure.api.v1.paginators.general_paginator import StandardResultsSetPagination, \
    LargeResultsSetPagination
from apps.search_engine.infrastructure.api.v1.serializers.article_serializers import ArticleSerializer


class ArticleViewSet(viewsets.ViewSet):
    serializer_class = ArticleSerializer
    pagination_class = StandardResultsSetPagination
    # Inject the service
    article_service = ArticleService()

    @extend_schema(
        description="List all articles",
        responses=ArticleSerializer(many=True),
        tags=['Articles']
    )
    def list(self, request, *args, **kwargs):
        try:
            page_number = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 100))

            articles = self.article_service.get_paginated_articles(page_number, page_size)
            total_articles = self.article_service.get_total_articles()

            serializer = ArticleSerializer(articles, many=True)

            has_more_articles = len(articles) == page_size

            next_page_url = None
            previous_page_url = None

            if has_more_articles:
                next_page_url = request.build_absolute_uri(
                    f"{request.path}?page={page_number + 1}&page_size={page_size}"
                )

            if page_number > 1:
                previous_page_url = request.build_absolute_uri(
                    f"{request.path}?page={page_number - 1}&page_size={page_size}"
                )

            return Response({
                'total': total_articles,
                'next_page_url': next_page_url,
                'previous_page_url': previous_page_url,
                'articles': serializer.data,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            clear_neo4j_database(db)
            return Response({'message': 'Database was cleaned'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleCount(APIView):
    # Inject the service
    article_service = ArticleService()

    @extend_schema(
        description="Get total number of articles",
        responses={'total_articles': int},
        tags=['Articles'],
    )
    def get(self, request, *args, **kwargs):
        try:
            article_count = self.article_service.get_total_articles()
            return Response({'total_articles': article_count, })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
