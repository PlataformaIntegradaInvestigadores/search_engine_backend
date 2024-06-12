from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from apps.search_engine.application.services.topic_service import TopicService
from apps.search_engine.infrastructure.api.v1.serializers.topic_serializer import TopicSerializer


class TopicViewSet(viewsets.ViewSet):
    # Inject Service
    topic_service = TopicService()

    @extend_schema(
        summary="Get all topics",
        responses={200: TopicSerializer(many=True)},
        tags=["Topics"]
    )
    def list(self, request):
        topics = self.topic_service.get_all_topics()
        serializer = TopicSerializer(topics, many=True).data
        return Response({"topics": serializer}, status=200)
