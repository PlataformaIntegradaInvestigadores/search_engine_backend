from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.dashboards.infrastructure.api.v1.views.populate_view import PopulateView

router = DefaultRouter()
router.register(r'', PopulateView, basename='populate-dashboard')
urlpatterns = [
    path('', PopulateView.as_view(), name='populate-dashboard'),
]