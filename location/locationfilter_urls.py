from django.urls import include, path
from rest_framework import routers
from django.contrib.auth.decorators import login_required


from location import views

router = routers.DefaultRouter()

router.register(r'', views.LocationAreaFilterViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('/map-locationfilter/', login_required(views.MapAreaFilterViewSet.as_view()), name="locationfilter-view"),
]
