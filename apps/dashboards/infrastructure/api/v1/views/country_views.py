from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dashboards.application.services.country_service import CountryService
from apps.dashboards.application.use_cases.country_acumulated_use_case import CountryAcumulatedUseCase
from apps.dashboards.application.use_cases.country_topics_acumulated_use_case import CountryTopicsAcumulatedUseCase
from apps.dashboards.application.use_cases.country_topics_use_case import CountryTopicsUseCase
from apps.dashboards.application.use_cases.country_topics_year_use_case import CountryTopicsYearUseCase
from apps.dashboards.application.use_cases.country_year_use_case import CountryYearUseCase
from apps.dashboards.application.use_cases.get_range_use_case import RangeUseCase
from apps.dashboards.application.use_cases.last_years_use_case import LastYearsUseCase
from apps.dashboards.application.use_cases.top_topics_by_year import TopTopicsByYearUseCase
from apps.dashboards.application.use_cases.top_topics_use_case import TopTopicsUseCase
from apps.dashboards.application.use_cases.year_info_use_case import YearInfoUseCase
from apps.dashboards.infrastructure.api.v1.serializers.country_acumulated_serializer import CountryAcumulatedSerializer
from apps.dashboards.infrastructure.api.v1.serializers.country_topics_serializer import CountryTopicsSerializer
from apps.dashboards.infrastructure.api.v1.serializers.country_topics_year_serializer import CountryTopicsYearSerializer
from apps.dashboards.infrastructure.api.v1.serializers.country_year_serializer import CountryYearSerializer


class CountryViews(viewsets.ModelViewSet):
    country_service = CountryService()

    @action(detail=False, methods=['get'])
    def get_topics(self, request):
        number_top = (request.query_params.get('number_top'))
        country_topics = CountryTopicsUseCase(country_service=self.country_service)
        data_topics = country_topics.execute(number_top=number_top)
        topics = CountryTopicsSerializer(data_topics, many=True)
        data = topics.data
        response_data = [
            {
                "text": topic['topic_name'],
                "size": topic['total_articles']
            }
            for topic in data
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_topics_year(self, request):
        topic = (request.query_params.get('topic'))
        year = (request.query_params.get('year'))
        country_topics_year = CountryTopicsYearUseCase(country_service=self.country_service)
        data_topics_year = country_topics_year.execute(topic=topic, year=year)
        topics_year = CountryTopicsYearSerializer(data_topics_year, many=True)
        return topics_year

    @action(detail=False, methods=['get'])
    def get_topics_acumulated(self, request):
        topic = (request.query_params.get('topic'))
        year = (request.query_params.get('year'))
        country_topics_acumulated = CountryTopicsAcumulatedUseCase(country_service=self.country_service)
        data_topics = country_topics_acumulated.execute(topic=topic, year=year)
        topics = CountryTopicsSerializer(data_topics, many=True)
        return topics

    @action(detail=False, methods=['get'])
    def get_acumulated(self, request):
        year = (request.query_params.get('year', 2023))
        country_acumulated = CountryAcumulatedUseCase(country_service=self.country_service)
        data_topics = country_acumulated.execute(year=year)
        serializer = CountryAcumulatedSerializer(data_topics, many=False)
        data = serializer.data
        response_data = {
            "author": data['total_authors'],
            "article": data['total_articles'],
            "affiliation": data['total_affiliations'],
            "topic": data['total_topics']
        }
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_year(self, request):
        year = (request.query_params.get('year'))
        year_use_case = CountryYearUseCase(country_service=self.country_service)
        year_response = year_use_case.execute(year)
        serializer = CountryYearSerializer(year_response)
        data = serializer.data
        print(data)
        response_data = {
            "author": data['total_authors'],
            "article": data['total_articles'],
            "affiliation": data['total_affiliations'],
            "topic": data['total_topics']
        }
        
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_top_topics(self, request):
        year = (request.query_params.get('year'))
        top_topics_use_case = TopTopicsUseCase(country_service=self.country_service)
        top_topics = top_topics_use_case.execute(year=year)
        serializer = CountryTopicsSerializer(top_topics, many=True)
        data = serializer.data
        response_data = [
            {
                "text": topic['topic_name'],
                "size": topic['total_articles']
            }
            for topic in data
        ]

        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_top_topics_year(self, request):
        year = (request.query_params.get('year'))
        top_topics_by_year_use_case = TopTopicsByYearUseCase(country_service=self.country_service)
        top_by_year = top_topics_by_year_use_case.execute(year=year)
        serializer = CountryTopicsYearSerializer(top_by_year, many=True)
        data = serializer.data
        response_data = [
            {
                "text": topic['topic_name'],
                "size": topic['total_articles']
            }
            for topic in data
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_last_years(self, request):
        last_years_use_case = LastYearsUseCase(country_service=self.country_service)
        last_years = last_years_use_case.execute()
        serializer = CountryYearSerializer(last_years, many=True)
        data = serializer.data
        response_data = [
            {
                'year': cy['year'],
                'author': cy['total_authors'],
                'article': cy['total_articles'],
                'affiliation': cy['total_affiliations'],
                'topic': cy['total_topics']
            }
            for cy in data
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_years(self, request):
        years_use_case = LastYearsUseCase(country_service=self.country_service)
        last_years = years_use_case.execute()
        serializer = CountryYearSerializer(last_years, many=True)
        data = serializer.data
        response_data = [
            {
                'year': cy['year'],
            }
            for cy in data
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_year_info(self, request):
        year = (request.query_params.get('year'))
        year_info_use_case = YearInfoUseCase(country_service=self.country_service)
        year_info = year_info_use_case.execute(year=year)
        serializer = CountryYearSerializer(year_info)
        cy = serializer.data
        response_data = [
            {
                'year': cy['year'],
                'author': cy['total_authors'],
                'article': cy['total_articles'],
                'affiliation': cy['total_affiliations'],
                'topic': cy['total_topics']
            }
        ]
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def get_range_info(self, request):
        year = (request.query_params.get('year'))
        range_use_case = RangeUseCase(country_service=self.country_service)
        year_info = range_use_case.execute(year=year)
        serializer = CountryYearSerializer(year_info, many=True)
        data = serializer.data
        response_data = [
            {
                'year': cy['year'],
                'author': cy['total_authors'],
                'article': cy['total_articles'],
                'affiliation': cy['total_affiliations'],
                'topic': cy['total_topics']
            }
            for cy in data
        ]
        return Response(response_data)