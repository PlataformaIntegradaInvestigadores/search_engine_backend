from django.urls import path
from .views import TextVectorizeView, TextProcessingHealthView

app_name = 'text_processing'

urlpatterns = [
    path('vectorize/', TextVectorizeView.as_view(), name='vectorize'),
    path('health/', TextProcessingHealthView.as_view(), name='health'),
]
