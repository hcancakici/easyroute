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
        user_filter = self.request.query_params.get('user_filter', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        try:
            radius = int(self.request.query_params.get('radius')) / 10  # KM
        except Exception as e:
            print(e)
            radius = None

        try:
            knn = int(self.request.query_params.get('knn'))
        except Exception as e:
            print(e)
            knn = None

        try:
            lat = float(self.request.query_params.get('lat'))
            lng = float(self.request.query_params.get('lng'))
            point = Point(lng, lat)
            point.srid = 4326
        except Exception as e:
            print(e)
            point = None

        if self.request.user and self.request.user.is_superuser:
            queryset = Location.objects.all()
            if user_filter:
                queryset = queryset.filter(username=user_filter)

        else:
            queryset = Location.objects.filter(username=self.request.user.username)

        if from_date is not None:
            try:
                from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
                queryset = queryset.filter(location_date__gte=from_date)
            except Exception as e:
                print(e)
                pass
        if to_date is not None:
            try:
                to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
                queryset = queryset.filter(location_date__lte=to_date)
            except Exception as e:
                print(e)
                pass

        if point and radius is not None:
            queryset = queryset.filter(location__distance_lt=(point, Distance(km=radius)))

        if point and knn is not None:
            queryset = queryset.annotate(distance=func_Distance('location', point)).order_by('distance')
            closest_routes = []
            for loc in queryset:
                if len(closest_routes) == knn:
                    break
                if loc.route_id not in closest_routes:
                    closest_routes.append(loc.route_id)

            queryset = queryset.filter(route_id__in=closest_routes).order_by('location_date')

        return queryset

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(self._group_by_route(queryset))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(self._group_by_route(queryset))

    def _group_by_route(self, queryset):
        groups = {}
        routes = set(queryset.values_list("route_id", flat=True))
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
        if request.user:
            if request.user.is_superuser:
                user_count = User.objects.count()
                point_count = Location.objects.filter(
                    is_active=True,
                    username__isnull=False,
                    route_id__isnull=False).count()
                route_count = len(set(Location.objects.values_list("route_id", flat=True)))
                user_list = User.objects.all()
            else:
                user_count = 1
                points = Location.objects.filter(
                    is_active=True,
                    route_id__isnull=False,
                    username=request.user.username)
                route_count = len(set(points.values_list("route_id", flat=True)))
                point_count = points.count()
                user_list = {}

            return Response({"user_count": user_count, "point_count": point_count, "route_count": route_count, "user_list": user_list}, template_name="newfile.html")
        return Response({}, template_name="newfile.html")


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
