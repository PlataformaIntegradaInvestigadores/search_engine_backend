from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.dashboards.infrastructure.api.v1.views.affiliation_views import AffiliationViewSet

router = DefaultRouter()
router.register(r'', AffiliationViewSet, basename='affiliation-dashboard')
urlpatterns = [
    path('', include(router.urls))
]
