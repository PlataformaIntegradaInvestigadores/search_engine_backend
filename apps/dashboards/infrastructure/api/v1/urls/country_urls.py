from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.dashboards.infrastructure.api.v1.views.country_views import CountryViews

router = DefaultRouter()
router.register(r'', CountryViews, basename='country-dashboard')
urlpatterns = [
    path('', include(router.urls))
]
