from rest_framework import serializers


class AffiliationSerializer(serializers.Serializer):
    name = serializers.CharField()
