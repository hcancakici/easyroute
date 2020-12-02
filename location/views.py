from rest_framework import viewsets

from location.serializers import LocationSerializer, LocationUserSerializer
from location.models import Location, LocationUser



class LocationUserViewSet(viewsets.ModelViewSet):
    queryset = LocationUser.objects.all()
    serializer_class = LocationUserSerializer
    ordering_fields = '__all__'


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    ordering_fields = '__all__'
