from django.urls import path, include

urlpatterns = [
    #path('author/', include('apps.dashboards.infrastructure.api.v1.urls.author_urls'), name='authors'),
    path('populate', include('apps.dashboards.infrastructure.api.v1.urls.populate_urls'), name='populate'),
    path('country/', include('apps.dashboards.infrastructure.api.v1.urls.country_urls'), name='country'),
    path('affiliation/', include('apps.dashboards.infrastructure.api.v1.urls.affiliation_urls'), name='affiliation'),
    path('province/', include('apps.dashboards.infrastructure.api.v1.urls.province_urls'), name='province'),
]
