from django.contrib import admin
from django.urls import include, path

from location import urls as location_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('locations', include(location_urls)),
    path('accounts/', include('django.contrib.auth.urls')),
]
