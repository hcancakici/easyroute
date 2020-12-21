from rest_framework import viewsets, generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


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


class MapViewSet(generics.RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    template_name = "map2.html"
    renderer_classes = [TemplateHTMLRenderer]
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return Response({'data': "data"}, template_name="map2.html")
