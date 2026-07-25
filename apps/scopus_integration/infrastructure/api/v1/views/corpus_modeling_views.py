from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings


class GenerateCorpusView(APIView):
    @extend_schema(
        summary='Generate corpus',
        tags=['TF-IDF'],
    )
    def post(self, request):
        try:
            if settings.USE_ML_MODELS_SERVICE:
                from apps.scopus_integration.medallion.pipeline import ScopusMedallionPipeline

                pipeline = ScopusMedallionPipeline()
                silver_result = pipeline.run_silver()
                gold_result = pipeline.run_gold()
                documents = pipeline.get_gold_ml_documents()
                return Response(
                    {
                        'success': True,
                        'total': len(documents),
                        'source': 'gold_ml_features',
                        'silver': silver_result,
                        'gold': gold_result,
                    },
                    status=status.HTTP_200_OK,
                )

            import pandas as pd
            from sklearn.feature_extraction.text import TfidfVectorizer
            from unidecode import unidecode
            import nltk
            from string import punctuation
            from nltk.corpus import stopwords

            from apps.scopus_integration.application.services.corpus_generation_service import CorpusService
            from apps.scopus_integration.application.usecases.generate_corpus_usecase import GenerateCorpusUseCase

            nltk.download('stopwords')

            corpus_path = 'resources/corpus/'
            modelo = 'tf-idf'
            version = 'v10.0'
            corpus_name = corpus_path + 'corpus-' + modelo + "-" + version + ".pkl"

            corpus_service = CorpusService()

            tokenizer = TfidfVectorizer().build_tokenizer()

            stop_words = [unidecode(stopW) for stopW in stopwords.words('english')]
            non_words = list(punctuation)
            non_words.extend(['¿', '¡', '...', '..'])
            stop_words = stop_words + non_words

            data = GenerateCorpusUseCase(corpus_service=corpus_service).execute()

            for article in data:
                article['preprocessed_doc'] = ' '.join(
                    [word.lower() for word in tokenizer(unidecode(article['doc'])) if word.lower() not in stop_words])

            pd.DataFrame(data)[['doc_id', 'preprocessed_doc']].to_pickle(corpus_name)

            df_corpus = pd.read_pickle(corpus_name)

            total = len(df_corpus)

            return Response({'success': True, 'total': total},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
