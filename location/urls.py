from django.urls import include, path
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


from location import views


router = routers.DefaultRouter()
router.register(r'', views.LocationViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('/map/', login_required(views.MapViewSet.as_view()), name="map-view"),
    path('/signup/', csrf_exempt(views.signup), name='signup'),
]
