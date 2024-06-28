from rest_framework import serializers


class AffiliationSerializer(serializers.Serializer):
    scopus_id = serializers.CharField()
    name = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()


class AffiliationNameSerializer(serializers.Serializer):
    name = serializers.CharField()
