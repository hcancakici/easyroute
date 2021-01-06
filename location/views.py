import datetime

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance, D

from rest_framework import viewsets, generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

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


class MapViewSet(generics.ListAPIView):
    serializer_class = LocationSerializer
    template_name = "map2.html"
    renderer_classes = [TemplateHTMLRenderer]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', 9)
        queryset = Location.objects.filter(user_id=user_id)
        queryset = Location.objects.all()
        date = self.request.query_params.get('date', None)
        radius = self.request.query_params.get('radius', 50000)  # KM
        knn = self.request.query_params.get('knn', 5)  # Check
        point = self.request.query_params.get('point', {"longitude": 41.07253, "latitude": 35.95237})

        if date is not None and False:
            try:
                date_dt2 = datetime.datetime.strptime(date, '%d-%m-%Y')
                queryset = queryset.filter(location_date__day=date_dt2.day,
                                           location_date__month=date_dt2.month,
                                           location_date__year=date_dt2.year)
            except Exception as e:
                print(e)
                pass

        if point:
            point = Point(point['longitude'], point['latitude'])

        if radius is not None:
            queryset = queryset.filter(location__distance_lt=(point, Distance(km=radius)))

        if knn is not None:
            queryset = queryset.filter(location__distance_lte=(point, D(km=radius)))
            queryset = queryset[:knn]

        return queryset

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = LocationSerializer(qs, many=True)
        return Response({'locations': serializer.data}, template_name="map2.html")
