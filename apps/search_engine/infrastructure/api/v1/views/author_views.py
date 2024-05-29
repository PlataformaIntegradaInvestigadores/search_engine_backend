from builtins import set

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.search_engine.domain.entities.author import Author
from apps.search_engine.infrastructure.api.v1.serializers.author_serializers import AuthorSerializer


class AuthorViews(APIView):
    def get(self, request):
        authors = Author.nodes.all()
        serializer = AuthorSerializer(authors, many=True).data
        return Response({'author': 'all authors', 'data': serializer})
