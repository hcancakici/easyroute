from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import include, path

from location import urls as location_urls
from location import density_urls
from location import locationfilter_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('locations', include(location_urls)),
    path('density', include(density_urls)),
    path('locationfilter', include(locationfilter_urls)),
    path('accounts/', include('django.contrib.auth.urls')),
] + staticfiles_urlpatterns()
