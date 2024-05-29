from rest_framework import serializers


class ArticleSerializer(serializers.Serializer):
    title = serializers.CharField()
    abstract = serializers.CharField()
    doi = serializers.CharField()
    publication_date = serializers.CharField()
    author_count = serializers.IntegerField()
    affiliation_count = serializers.IntegerField()
    corpus = serializers.CharField()
    affiliations = serializers.SerializerMethodCharField()
    topics = serializers.SerializerMethodCharField()


