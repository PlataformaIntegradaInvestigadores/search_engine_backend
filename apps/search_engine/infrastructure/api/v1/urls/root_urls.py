from django.urls import path, include

urlpatterns = [
    path('authors/', include('apps.search_engine.infrastructure.api.v1.urls.author_urls'), name='authors'),
    path('articles/', include('apps.search_engine.infrastructure.api.v1.urls.article_urls'), name='articles'),
    path('topics/', include('apps.search_engine.infrastructure.api.v1.urls.topic_urls'), name='topics'),
]
