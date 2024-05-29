from django.urls import path, include

urlpatterns = [
    path('authors/', include('apps.search_engine.infrastructure.api.v1.urls.author_urls'), name='authors'),
]
