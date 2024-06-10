from rest_framework import serializers


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
