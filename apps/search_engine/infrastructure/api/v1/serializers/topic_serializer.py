from rest_framework import serializers


class TopicSerializer(serializers.Serializer):
    name = serializers.CharField()
