from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.scopus_integration.application.services.model_generation_service import ModelGenerationService


class GenerateModelView(APIView):
    def post(self, request):
        try:
            model_generator = ModelGenerationService()
            corpus = model_generator.read_path()
            model_generator.generate_model(corpus)
            return Response({'status': 'success'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
