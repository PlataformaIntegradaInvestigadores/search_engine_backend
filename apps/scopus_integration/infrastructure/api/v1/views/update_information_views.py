from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.scopus_integration.application.services.AuthorServicePort import AuthorServicePort
from apps.scopus_integration.application.services.scopus_client import ScopusClient
from apps.scopus_integration.application.usecases.update_author_information_usecase import \
    UpdateAuthorInformationUseCase


class UpdateInformationViewSet(viewsets.ViewSet):
    client = ScopusClient()
    author_repository = AuthorServicePort()

    @action(detail=False, methods=['post'], url_path='author-information', url_name='update-author-information')
    def update_author_information(self, request, *args, **kwargs):
        try:
            update_author_information_usecase = UpdateAuthorInformationUseCase(author_repository=self.author_repository,
                                                                               client=self.client)
            total = update_author_information_usecase.execute()
            return Response({'message': f'{total} Authors updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
