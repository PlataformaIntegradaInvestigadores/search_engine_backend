from rest_framework.routers import DefaultRouter

from apps.scopus_integration.infrastructure.api.v1.views.logger_views import LoggerViewSet

router = DefaultRouter()
router.register('logs', LoggerViewSet, basename='logs')
urlpatterns = router.urls
