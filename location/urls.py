from rest_framework import routers

from location import views 


router = routers.DefaultRouter()
router.register(r'', views.LocationViewSet)

urlpatterns = router.urls

