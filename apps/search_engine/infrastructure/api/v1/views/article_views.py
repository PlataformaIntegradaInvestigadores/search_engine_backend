from drf_spectacular.utils import extend_schema, OpenApiParameter
from neomodel import clear_neo4j_database, db
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from apps.search_engine.application.services.article_service import ArticleService
from apps.search_engine.application.usecases.article.article_by_id_usecase import ArticleByIdUseCase
from apps.search_engine.application.usecases.article.list_all_articles_usecase import ListAllArticlesUseCase
from apps.search_engine.application.usecases.article.most_relevant_articles_by_topic_usecase import \
    MostRelevantArticlesUseCase
from apps.search_engine.application.usecases.article.total_articles_usecase import TotalArticlesUseCase
from apps.search_engine.infrastructure.api.v1.serializers.article_serializers import ArticleSerializer, \
    MostRelevantArticlesRequestSerializer, MostRelevantArticleResponseSerializer, \
    MostRelevantArticlesResponseSerializer, YearsSerializer
from apps.search_engine.infrastructure.api.v1.utils.build_paginator import build_pagination_urls


class ArticleViewSet(viewsets.ViewSet):
    serializer_class = ArticleSerializer

    # Inject the service
    article_service = ArticleService()

    @extend_schema(
        description="List all articles",
        responses=ArticleSerializer(many=True),
        tags=['Articles'],
        parameters=[
            OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number'),
            OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Page size'),
        ]
    )
    def list(self, request, *args, **kwargs):
        try:
            page_number = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))

            # Inject the use cases
            list_article_use_case = ListAllArticlesUseCase(article_repository=self.article_service)
            total_articles_use_case = TotalArticlesUseCase(article_repository=self.article_service)

            # Execute the use cases
            articles = list_article_use_case.execute(page_number, page_size)
            total_articles = total_articles_use_case.execute()

            serializer = ArticleSerializer(articles, many=True)

            pagination_info = build_pagination_urls(request, page_number, page_size, articles)

            return Response({
                'total': total_articles,
                'next_page': pagination_info.get('next_page'),
                'previous_page': pagination_info.get('previous_page'),
                'articles': serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            clear_neo4j_database(db)
            return Response({'message': 'Database was cleaned'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Retrieve an article by ID",
        responses=ArticleSerializer,
        tags=['Articles'],
    )
    def retrieve(self, request, *args, **kwargs):
        try:

            article_id = kwargs.get('pk')
            # Inject the use case
            article_by_id_use_case = ArticleByIdUseCase(article_repository=self.article_service)

            article = article_by_id_use_case.execute(article_id)
            serializer = ArticleSerializer(article)
            authors = self.article_service.find_authors_by_article(article_id)
            data = serializer.data
            data['authors'] = authors[0]

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get most relevant articles by topic",
        tags=['Articles'],
        request=MostRelevantArticlesRequestSerializer,
        summary="Get most relevant articles by topic",
    )
    @action(detail=False, methods=['post'], url_path='most-relevant-articles-by-topic')
    def most_relevant_articles_by_topic(self, request, *args, **kwargs):
        try:
            serializer = MostRelevantArticlesRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            topic = serializer.validated_data.get('query')
            page = int(serializer.validated_data.get('page'))
            size = int(serializer.validated_data.get('size'))
            custom_type = serializer.validated_data.get('type')
            custom_years = serializer.validated_data.get('years')

            most_relevant_articles_usecase = MostRelevantArticlesUseCase(article_repository=self.article_service)
            df, years = most_relevant_articles_usecase.execute(topic, page, size)
            df = [str(article) for article in df]
            if custom_type:
                filtered_articles = self.article_service.find_articles_by_filter_years(custom_type, custom_years,
                                                                                       df)
                filtered_ids = [f"{article.scopus_id}" for article in filtered_articles]
                articles, total_articles = self.article_service.find_articles_by_ids(filtered_ids, page, size)

            else:
                articles, total_articles = self.article_service.find_articles_by_ids(df, page, size)
            article_serializer = MostRelevantArticleResponseSerializer(articles, many=True)

            years_data = [int(year.split("-")[0]) for year in years]
            return Response(
                {'data': article_serializer.data, 'years': set(years_data), 'total': total_articles},
                status=status.HTTP_200_OK)
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
            article_count = self.article_service.find_total_articles()
            return Response({'total_articles': article_count, })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
