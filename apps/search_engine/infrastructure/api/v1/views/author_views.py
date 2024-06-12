from builtins import set

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.search_engine.application.services.author_service import AuthorService
from apps.search_engine.application.usecases.list_all_authors import ListAllAuthorsUseCase
from apps.search_engine.domain.entities.author import Author
from apps.search_engine.infrastructure.api.v1.serializers.author_serializers import AuthorSerializer


class AuthorViews(APIView):
    # inject the service
    author_service = AuthorService()

    @extend_schema(
        description="List all authors",
        responses=AuthorSerializer(many=True),
        tags=['Authors'],
        parameters=[
            OpenApiParameter(name='page_size', type=int, required=False),
            OpenApiParameter(name='page', type=int, required=False)
        ]
    )
    def get(self, request):
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))

        # inject use cases
        list_author_use_case = ListAllAuthorsUseCase(author_service=self.author_service)

        # execute the use cases
        authors = list_author_use_case.execute(page_size=page_size, page=page)
        serializer = AuthorSerializer(authors, many=True)

        data = serializer.data

        return Response({'author': 'all authors', 'data': data})
