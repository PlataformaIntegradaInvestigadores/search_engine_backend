from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.search_engine.infrastructure.api.v1.views.author_views import AuthorViews

router = DefaultRouter()
router.register(r'authors', AuthorViews, basename='author')
# urlpatterns = [
#     path('', AuthorViews.as_view(), name='authors'),
#     path('find_by_query/', AuthorViews.as_view({'get': 'find_by_query'}), name='find_by_query'),
# ]
urlpatterns = router.urls
