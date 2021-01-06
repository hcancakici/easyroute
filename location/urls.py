from django.urls import include, path
from rest_framework import routers

from location import views


router = routers.DefaultRouter()
router.register(r'', views.LocationViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('/map/', views.MapViewSet.as_view(), name="map-view"),
]
