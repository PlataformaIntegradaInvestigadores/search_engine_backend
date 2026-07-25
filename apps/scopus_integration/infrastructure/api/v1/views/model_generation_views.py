from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from apps.scopus_integration.infrastructure.clients.ml_models_client import MLModelsClient
from apps.scopus_integration.application.services.model_generation_service import ModelGenerationService
from apps.scopus_integration.medallion.pipeline import ScopusMedallionPipeline


class GenerateModelView(APIView):
    @extend_schema(
        summary='Generate model',
        tags=['TF-IDF'],
    )
    def post(self, request):
        try:
            if settings.USE_ML_MODELS_SERVICE:
                pipeline = ScopusMedallionPipeline()
                documents = pipeline.get_gold_ml_documents()
                if not documents:
                    pipeline.run_silver()
                    pipeline.run_gold()
                    documents = pipeline.get_gold_ml_documents()
                if not documents:
                    return Response(
                        {
                            'success': False,
                            'message': 'No hay documentos Gold para construir el modelo. Extrae datos de Scopus y genera el corpus primero.',
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                result = MLModelsClient().build_tfidf(documents=documents, version='v10.0')
                return Response({'success': True, **result}, status=status.HTTP_200_OK)

            model_generator = ModelGenerationService()
            corpus = model_generator.read_path()
            model_generator.generate_model(corpus)
            return Response({'success': True},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
