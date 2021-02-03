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
    path('/map-busy/', login_required(views.MapBusyViewSet.as_view()), name="busy-view"),
    path('/signup', csrf_exempt(views.signup), name='signup'),
    path('/friend_list', views.friend_list, name='friend-list'),
    path('/get_user_route_count', views.get_user_route_count, name='user-route-count'),
    path('/friend_list_detail', login_required(views.FriendListViewSet.as_view()), name='friend-list-detail'),
]
