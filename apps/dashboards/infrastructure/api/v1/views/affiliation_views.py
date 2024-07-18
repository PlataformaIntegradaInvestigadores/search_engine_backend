from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiExample
from mongoengine import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dashboards.application.services.affiliation_service import AffiliationService
from apps.dashboards.application.use_cases.affiliation_last_years_use_case import AffiliationLastYearsUseCase
from apps.dashboards.application.use_cases.get_affiliations_acumulated_use_case import AffiliationsAcumulatedUseCase
from apps.dashboards.application.use_cases.get_affiliations_use_case import AffiliationsUseCase
from apps.dashboards.application.use_cases.get_affiliations_year_acumulated import AffiliationsYearUseCase
from apps.dashboards.domain.entities.affiliation import Affiliation
from apps.dashboards.domain.entities.affiliation_topics import AffiliationTopics
from apps.dashboards.domain.entities.affiliation_topics_acumulated import AffiliationTopicsAcumulated
from apps.dashboards.domain.entities.affiliation_topics_year import AffiliationTopicsYear
from apps.dashboards.domain.entities.affiliation_year import AffiliationYear
from apps.dashboards.domain.entities.affiliation_year_acumulated import AffiliationAcumulated
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_acumulated_serializer import \
    AffiliationAcumulatedSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_serializer import AffiliationSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_topic_serializer import \
    AffiliationTopicYearSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_topics_acumulated_serializer import \
    AffiliationTopicAcumulatedSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_topics_serializer import AffiliationTopicsSerializer
from apps.dashboards.infrastructure.api.v1.serializers.affiliation_year_serializer import AffiliationYearSerializer


class AffiliationViewSet(viewsets.ModelViewSet):
    affiliation_service = AffiliationService()

    @extend_schema(
        description="Get affiliation by name",
        responses=AffiliationSerializer,
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='name', type=str, location=OpenApiParameter.QUERY, description='Affiliation name')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_by_name(self, request):
        try:
            name = request.query_params.get('name')
            aff = Affiliation.objects.get(name=name)
            serializer = AffiliationSerializer(aff)
            data = serializer.data
            response_data = {
                "scopus_id": data['scopus_id'],
            }
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get top affiliations by year",
        responses=AffiliationAcumulatedSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_top_affiliations(self, request):
        try:
            year = request.query_params.get('year')
            affiliations_use_case = AffiliationsAcumulatedUseCase(affiliations_service=self.affiliation_service)
            affiliations = affiliations_use_case.execute(year=year)
            serializer = AffiliationAcumulatedSerializer(affiliations, many=True)
            data = serializer.data
            response_data = [
                {
                    "text": affiliation['name'],
                    "size": affiliation['total_articles']
                }
                for affiliation in data
            ]
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get all affiliations",
        responses=AffiliationSerializer(many=True),
        tags=['Affiliations']
    )
    @action(detail=False, methods=['get'])
    def get_affiliations(self, request):
        try:
            affiliations_use_case = AffiliationsUseCase(affiliations_service=self.affiliation_service)
            affiliations = affiliations_use_case.execute()
            serializer = AffiliationSerializer(affiliations, many=True)
            data = serializer.data
            response_data = [
                {
                    "text": affiliation['name'],
                    "size": affiliation['total_articles']
                }
                for affiliation in data
            ]
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get top affiliations by year",
        responses=AffiliationYearSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_top_affiliations_year(self, request):
        try:
            year = request.query_params.get('year')
            affiliations_year_use_case = AffiliationsYearUseCase(affiliations_service=self.affiliation_service)
            affiliations = affiliations_year_use_case.execute(year=year)
            serializer = AffiliationYearSerializer(affiliations, many=True)
            data = serializer.data
            response_data = [
                {
                    "text": affiliation['name'],
                    "size": affiliation['total_articles']
                }
                for affiliation in data
            ]
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Search affiliations",
        responses=AffiliationSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='query', type=str, location=OpenApiParameter.QUERY, description='Search query')
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        try:
            query = request.GET.get('query', '')
            affiliations = Affiliation.objects.filter(Q(name__icontains=query)).order_by('-total_articles')
            result = [
                {
                    'scopus_id': affiliation.scopus_id,
                    'name': affiliation.name,
                    'total_articles': affiliation.total_articles
                } for affiliation in affiliations
            ]
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get affiliation years",
        responses=AffiliationYearSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_affiliation_years(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            affiliation = AffiliationYear.objects(scopus_id=scopus_id).filter(year__gt=1999).order_by('year')
            serializer = AffiliationYearSerializer(affiliation, many=True)
            data = serializer.data
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get affiliation topics",
        responses=AffiliationTopicsSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_affiliation_topics(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            affiliation_topics = AffiliationTopics.objects(scopus_id=scopus_id).filter(topic_name__ne=" ").filter(
                topic_name__ne='').order_by('-total_articles')[:20]
            serializer = AffiliationTopicsSerializer(affiliation_topics, many=True)
            data = serializer.data
            response_data = [
                {
                    "text": topic['topic_name'],
                    "size": topic['total_articles']
                }
                for topic in data
            ]
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get last years of affiliation",
        responses=AffiliationYearSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_years(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            last_years_use_case = AffiliationLastYearsUseCase(affiliation_service=self.affiliation_service)
            last_years = last_years_use_case.execute(scopus_id=scopus_id)
            serializer = AffiliationYearSerializer(last_years, many=True)
            data = serializer.data
            response_data = [
                {
                    'year': aff['year'],
                }
                for aff in data
            ]
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get number of articles and topics for an affiliation",
        responses=OpenApiExample(
            'Articles and topics count',
            {
                "articles": 100,
                "topics": 20
            }
        ),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_articles_topics(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            num_articles_s = Affiliation.objects.get(scopus_id=scopus_id)
            num_articles = AffiliationSerializer(num_articles_s)
            num_topics_s = AffiliationTopics.objects(scopus_id=scopus_id).filter(topic_name__ne=" ").filter(
                topic_name__ne='').count()
            response_data = {
                'articles': num_articles.data['total_articles'],
                'topics': num_topics_s
            }
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get number of articles and topics for an affiliation by year",
        responses=OpenApiExample(
            'Articles and topics count by year',
            {
                "articles": 100,
                "topics": 20
            }
        ),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID'),
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_articles_topics_year(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            year = request.query_params.get('year')
            num_articles_s = AffiliationYear.objects.get(scopus_id=scopus_id, year=year)
            num_articles = AffiliationYearSerializer(num_articles_s)

            num_topics_s = AffiliationTopicsYear.objects(scopus_id=scopus_id, year=year).filter(topic_name__ne=" ").filter(
                topic_name__ne='').count()
            response_data = {
                'articles': num_articles.data['total_articles'],
                'topics': num_topics_s
            }
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get number of articles and topics accumulated for an affiliation by year",
        responses=OpenApiExample(
            'Articles and topics accumulated by year',
            {
                "articles": 100,
                "topics": 20
            }
        ),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID'),
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_articles_topics_acumulated(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            year = request.query_params.get('year')
            num_articles_s = AffiliationAcumulated.objects.get(scopus_id=scopus_id, year=year)
            num_articles = AffiliationAcumulatedSerializer(num_articles_s)
            response_data = {
                'articles': num_articles.data['total_articles'],
                'topics': num_articles.data['total_topics']
            }
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get accumulated topics for an affiliation by year",
        responses=AffiliationTopicAcumulatedSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID'),
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_topics_acumulated(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            year = request.query_params.get('year')
            topics_s = AffiliationTopicsAcumulated.objects(scopus_id=scopus_id, year=year).filter(
                topic_name__ne=" ").filter(topic_name__ne='').order_by(
                "-total_articles")[:30]
            serializer = AffiliationTopicAcumulatedSerializer(topics_s, many=True)
            topics = serializer.data
            response_data = [
                {
                    "text": topic['topic_name'],
                    "size": topic['total_articles']
                }
                for topic in topics
            ]
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get topics for an affiliation by year",
        responses=AffiliationTopicYearSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID'),
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_topics_year(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            year = request.query_params.get('year')
            topics_s = AffiliationTopicsYear.objects(scopus_id=scopus_id, year=year).filter(topic_name__ne=" ").filter(
                topic_name__ne='').order_by(
                "-total_articles")[:30]
            serializer = AffiliationTopicYearSerializer(topics_s, many=True)
            topics = serializer.data
            response_data = [
                {
                    "text": topic['topic_name'],
                    "size": topic['total_articles']
                }
                for topic in topics
            ]
            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get affiliation details for a specific year",
        responses=AffiliationYearSerializer,
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID'),
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_year(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            year = request.query_params.get('year')
            year_s = AffiliationYear.objects.get(scopus_id=scopus_id, year=year)
            serializer = AffiliationYearSerializer(year_s)
            topics = serializer.data
            return Response([topics])
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Get affiliation details for a range of years",
        responses=AffiliationYearSerializer(many=True),
        tags=['Affiliations'],
        parameters=[
            OpenApiParameter(name='scopus_id', type=str, location=OpenApiParameter.QUERY, description='Scopus ID'),
            OpenApiParameter(name='year', type=str, location=OpenApiParameter.QUERY, description='Year')
        ]
    )
    @action(detail=False, methods=['get'])
    def get_year_range(self, request):
        try:
            scopus_id = request.query_params.get('scopus_id')
            year = request.query_params.get('year')
            year_s = AffiliationYear.objects(scopus_id=scopus_id).filter(year__gt=1999, year__lte=year).order_by('year')
            serializer = AffiliationYearSerializer(year_s, many=True)
            topics = serializer.data
            return Response(topics)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class AffiliationViewSet(viewsets.ModelViewSet):
#     affiliation_service = AffiliationService()
#
#     @action(detail=False, methods=['get'])
#     def get_by_name(self, request):
#         name = (request.query_params.get('name'))
#         aff = Affiliation.objects.get(name=name)
#         serializer = AffiliationSerializer(aff)
#         data = serializer.data
#         response_data = {
#                 "scopus_id": data['scopus_id'],
#             }
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_top_affiliations(self, request):
#         year = (request.query_params.get('year'))
#         affiliations_use_case = AffiliationsAcumulatedUseCase(affiliations_service=self.affiliation_service)
#         affiliations = affiliations_use_case.execute(year=year)
#         serializer = AffiliationAcumulatedSerializer(affiliations, many=True)
#         data = serializer.data
#         response_data = [
#             {
#                 "text": affiliation['name'],
#                 "size": affiliation['total_articles']
#             }
#             for affiliation in data
#         ]
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_affiliations(self, request):
#         affiliations_use_case = AffiliationsUseCase(affiliations_service=self.affiliation_service)
#         affiliations = affiliations_use_case.execute()
#         serializer = AffiliationSerializer(affiliations, many=True)
#         data = serializer.data
#         response_data = [
#             {
#                 "text": affiliation['name'],
#                 "size": affiliation['total_articles']
#             }
#             for affiliation in data
#         ]
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_top_affiliations_year(self, request):
#         year = (request.query_params.get('year'))
#         affiliations_year_use_case = AffiliationsYearUseCase(affiliations_service=self.affiliation_service)
#         affiliations = affiliations_year_use_case.execute(year=year)
#         serializer = AffiliationYearSerializer(affiliations, many=True)
#         data = serializer.data
#         response_data = [
#             {
#                 "text": affiliation['name'],
#                 "size": affiliation['total_articles']
#             }
#             for affiliation in data
#         ]
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def search(self, request):
#         query = request.GET.get('query', '')
#         affiliations = Affiliation.objects.filter(Q(name__icontains=query)).order_by('-total_articles')
#         result = [
#             {
#                 'scopus_id': affiliation.scopus_id,
#                 'name': affiliation.name,
#                 'total_articles': affiliation.total_articles
#             } for affiliation in affiliations
#         ]
#         return Response(result)
#
#     @action(detail=False, methods=['get'])
#     def get_affiliation_years(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         affiliation = AffiliationYear.objects(scopus_id=scopus_id).filter(year__gt=1999).order_by('year')
#         serializer = AffiliationYearSerializer(affiliation, many=True)
#         data = serializer.data
#         return Response(data)
#
#     @action(detail=False, methods=['get'])
#     def get_affiliation_topics(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         affiliation_topics = AffiliationTopics.objects(scopus_id=scopus_id).filter(topic_name__ne=" ").filter(
#             topic_name__ne='').order_by(
#             '-total_articles')[:20]
#         serializer = AffiliationTopicsSerializer(affiliation_topics, many=True)
#         data = serializer.data
#         response_data = [
#             {
#                 "text": topic['topic_name'],
#                 "size": topic['total_articles']
#             }
#             for topic in data
#         ]
#
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_years(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         last_years_use_case = AffiliationLastYearsUseCase(affiliation_service=self.affiliation_service)
#         last_years = last_years_use_case.execute(scopus_id=scopus_id)
#         serializer = AffiliationYearSerializer(last_years, many=True)
#         data = serializer.data
#         response_data = [
#             {
#                 'year': aff['year'],
#             }
#             for aff in data
#         ]
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_articles_topics(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         num_articles_s = Affiliation.objects.get(scopus_id=scopus_id)
#         num_articles = AffiliationSerializer(num_articles_s)
#         num_topics_s = AffiliationTopics.objects(scopus_id=scopus_id).filter(topic_name__ne=" ").filter(
#             topic_name__ne='').count()
#         response_data = {
#             'articles': num_articles.data['total_articles'],
#             'topics': num_topics_s
#         }
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_articles_topics_year(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         year = (request.query_params.get('year'))
#         num_articles_s = AffiliationYear.objects.get(scopus_id=scopus_id, year=year)
#         num_articles = AffiliationYearSerializer(num_articles_s)
#
#         num_topics_s = AffiliationTopicsYear.objects(scopus_id=scopus_id, year=year).filter(topic_name__ne=" ").filter(
#             topic_name__ne='').count()
#         response_data = {
#             'articles': num_articles.data['total_articles'],
#             'topics': num_topics_s
#         }
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_articles_topics_acumulated(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         year = (request.query_params.get('year'))
#         num_articles_s = AffiliationAcumulated.objects.get(scopus_id=scopus_id, year=year)
#         num_articles = AffiliationAcumulatedSerializer(num_articles_s)
#         response_data = {
#             'articles': num_articles.data['total_articles'],
#             'topics': num_articles.data['total_topics']
#         }
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_topics_acumulated(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         year = (request.query_params.get('year'))
#         topics_s = AffiliationTopicsAcumulated.objects(scopus_id=scopus_id, year=year).filter(
#             topic_name__ne=" ").filter(topic_name__ne='').order_by(
#             "-total_articles")[:30]
#         serializer = AffiliationTopicAcumulatedSerializer(topics_s, many=True)
#         topics = serializer.data
#         response_data = [
#             {
#                 "text": topic['topic_name'],
#                 "size": topic['total_articles']
#             }
#             for topic in topics
#         ]
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_topics_year(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         year = (request.query_params.get('year'))
#         topics_s = AffiliationTopicsYear.objects(scopus_id=scopus_id, year=year).filter(topic_name__ne=" ").filter(
#             topic_name__ne='').order_by(
#             "-total_articles")[:30]
#         serializer = AffiliationTopicYearSerializer(topics_s, many=True)
#         topics = serializer.data
#         response_data = [
#             {
#                 "text": topic['topic_name'],
#                 "size": topic['total_articles']
#             }
#             for topic in topics
#         ]
#         return Response(response_data)
#
#     @action(detail=False, methods=['get'])
#     def get_year(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         year = (request.query_params.get('year'))
#         year_s = AffiliationYear.objects.get(scopus_id=scopus_id, year=year)
#         serializer = AffiliationYearSerializer(year_s)
#         topics = serializer.data
#         return Response([topics])
#
#     @action(detail=False, methods=['get'])
#     def get_year_range(self, request):
#         scopus_id = (request.query_params.get('scopus_id'))
#         year = (request.query_params.get('year'))
#         year_s = AffiliationYear.objects(scopus_id=scopus_id).filter(year__gt=1999, year__lte=year).order_by('year')
#         serializer = AffiliationYearSerializer(year_s, many=True)
#         topics = serializer.data
#         return Response(topics)
