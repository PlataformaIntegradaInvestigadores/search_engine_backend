from rest_framework import serializers

from apps.search_engine.domain.entities.author import Author


class AuthorSerializer(serializers.Serializer):
    scopus_id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    auth_name = serializers.CharField()
    initials = serializers.CharField()
    affiliations = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()
    co_authors = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()

    def get_affiliations(self, obj):
        return [affiliation.name for affiliation in obj.affiliations.all()]

    def get_co_authors(self, obj):
        return [co_author.auth_name for co_author in obj.co_authors.all()]

    def get_articles(self, obj):
        return [article.title for article in obj.articles.all()]

    def get_topics(self, obj):
        return [topic.name for topic in obj.topics.all()]
