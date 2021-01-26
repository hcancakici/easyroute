import datetime
import json

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as func_Distance

from django.http import HttpResponse

from rest_framework import viewsets, generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from location.serializers import LocationCreateSerializer, LocationListSerializer
from location.models import Location


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    ordering_fields = '__all__'

    def get_queryset(self):
        if self.request.user and self.request.user.is_superuser:
            queryset = Location.objects.all()
        else:
            queryset = Location.objects.filter(username=self.request.user.username)

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

        queryset = Location.objects.all()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(self._group_by_route(queryset))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(self._group_by_route(queryset))

    def _group_by_route(self, queryset):
        groups = {}
        routes = queryset.values_list("route_id", flat=True)
        for route in routes:
            groups[route] = LocationListSerializer(queryset.filter(route_id=route), many=True).data

        return groups

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LocationCreateSerializer

        return LocationListSerializer


class MapViewSet(generics.ListAPIView):
    serializer_class = LocationListSerializer
    template_name = "map2.html"
    renderer_classes = [TemplateHTMLRenderer]
    http_method_names = ['get', 'post']
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({}, template_name="map2.html")


def signup(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        try:
            username = body['username']
            password = body['password']
        except KeyError:
            return HttpResponse("404")

        user, is_created = User.objects.get_or_create(username=username, password=password)
        if is_created:
            user.set_password(password)

        user.save()
        login(request, user)
        return HttpResponse("201")

    return HttpResponse("404")
