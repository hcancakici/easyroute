import datetime

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as func_Distance


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

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', 9)
        queryset = Location.objects.filter(user_id=user_id)
        queryset = Location.objects.all()
        date = self.request.query_params.get('date', None)

        try:
            radius = int(self.request.query_params.get('radius'))  # KM
        except:
            radius = None
        try:
            knn = int(self.request.query_params.get('knn'))
        except:
            knn = None

        try:
            lat = float(self.request.query_params.get('lat'))
            lng = float(self.request.query_params.get('lng'))
            point = Point(lng, lat)
            point.srid = 4326
        except:
            point = None

        if date is not None and False:
            try:
                date_dt2 = datetime.datetime.strptime(date, '%Y-%m-%d')
                queryset = queryset.filter(location_date__day=date_dt2.day,
                                           location_date__month=date_dt2.month,
                                           location_date__year=date_dt2.year)
            except Exception as e:
                print(e)
                pass

        if point and radius is not None:
            queryset = queryset.filter(location__distance_lt=(point, Distance(km=radius)))

        if point and knn is not None:
            queryset = queryset.annotate(
                distance=func_Distance('location', point)
            ).order_by('distance')
            queryset = queryset[:knn]

        return queryset


class MapViewSet(generics.ListAPIView):
    serializer_class = LocationSerializer
    template_name = "map2.html"
    renderer_classes = [TemplateHTMLRenderer]
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return Response({}, template_name="map2.html")
