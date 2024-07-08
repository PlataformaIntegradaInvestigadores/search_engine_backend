from rest_framework import serializers
from datetime import datetime


class ArticleSerializer(serializers.Serializer):
    title = serializers.CharField()
    abstract = serializers.CharField()
    doi = serializers.CharField()
    publication_date = serializers.CharField()
    author_count = serializers.IntegerField()
    affiliation_count = serializers.IntegerField()
    corpus = serializers.CharField()
    affiliations = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()
    scopus_id = serializers.IntegerField()

    def get_affiliation_count(self, obj):
        return len(obj.affiliations.all())

    def get_affiliations(self, obj):
        return [affiliation.name for affiliation in obj.affiliations.all()]

    def get_topics(self, obj):
        return [topic.name for topic in obj.topics.all()]


class MostRelevantArticlesRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    type = serializers.CharField(required=False)
    years = serializers.ListField(child=serializers.CharField(), required=False)


class MostRelevantArticleResponseSerializer(serializers.Serializer):
    title = serializers.CharField()
    author_count = serializers.IntegerField()
    affiliation_count = serializers.IntegerField()
    publication_date = serializers.CharField()
    scopus_id = serializers.IntegerField()

    def get_affiliation_count(self, obj):
        return len(obj.affiliations.all())


class YearsSerializer(serializers.Serializer):
    year = serializers.CharField()

    def get_year(self, obj):
        return obj.year.split('-')[0]

    def to_representation(self, instance):
        date_str = self.validated_data['year']
        year = date_str.split('-')[0]

        return {'year': year}


class MostRelevantArticlesResponseSerializer(serializers.Serializer):
    data = MostRelevantArticleResponseSerializer(many=True)
    years = YearsSerializer(many=True)
    total = serializers.IntegerField()
