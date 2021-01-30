from django.urls import include, path
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


from location import views

router = routers.DefaultRouter()

router.register(r'', views.LocationBusyViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('/map-busy/', login_required(views.MapBusyViewSet.as_view()), name="busy-view"),
    path('/signup/', csrf_exempt(views.signup), name='signup-key'),
    path('/friend_list', views.friend_list, name='friend-list-key'),
    path('/friend_list_detail', login_required(views.FriendListViewSet.as_view()), name='friend-list-detail-key'),
]
