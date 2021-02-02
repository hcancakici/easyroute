import datetime
import json

from geopy.distance import distance
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as func_Distance

from django.http import HttpResponse
from django.http import JsonResponse


from rest_framework import viewsets, generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from location.serializers import LocationCreateSerializer, LocationListSerializer
from location.models import FriendList, Location


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    ordering_fields = '__all__'

    def get_queryset(self):
        user_filter = self.request.query_params.get('user_filter', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        friend_name = self.request.query_params.get('friend_name', None)
        route_filter = self.request.query_params.get('route_filter', None)
        route_filter = False if route_filter == 'null' else route_filter
        friend_filter = False
        if friend_name:
            try:
                friend_list = FriendList.objects.get(username=self.request.user.username).friend_list
            except:
                friend_list = []

            if friend_name in friend_list:
                friend_filter = True

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
            if friend_name:
                print("sa")
                print(friend_name)
                friend_filter = True
            queryset = Location.objects.all()
            if user_filter:
                queryset = queryset.filter(username=user_filter)
            elif friend_filter:
                queryset = queryset.filter(username=friend_filter)
        else:
            queryset = Location.objects.filter(username=self.request.user.username)

        friend_query = self._get_friend_query(friend_name if friend_filter else False)

        if from_date is not None:
            try:
                from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
                queryset = queryset.filter(location_date__gte=from_date)
                friend_query = friend_query.filter(location_date__gte=from_date)
            except Exception as e:
                print(e)
                pass
        if to_date is not None:
            try:
                to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
                queryset = queryset.filter(location_date__lte=to_date)
                friend_query = friend_query.filter(location_date__lte=to_date)
            except Exception as e:
                print(e)
                pass
        if radius:
            if point:
                queryset = queryset.filter(location__distance_lt=(point, Distance(km=radius)))
                friend_query = friend_query.filter(location__distance_lt=(point, Distance(km=radius)))
            elif route_filter and friend_filter:
                routes_filter_query = Location.objects.filter(route_id=route_filter)
                friend_query_routes = []
                for friend_query_location in friend_query:
                    for routes_filter_location in routes_filter_query:
                        if distance(friend_query_location.location, routes_filter_location.location) < radius:
                            if friend_query_location.route_id not in friend_query_routes:
                                friend_query_routes.append(friend_query_location.route_id)
                friend_query_routes.append(route_filter)
                friend_query_routes = set(friend_query_routes)
                friend_query = friend_query.filter(route_id__in=friend_query_routes)
                queryset = queryset.filter(route_id__in=friend_query_routes)
            '''
            bug var
            elif route_filter:
                print(route_filter)
                routes_filter_query = Location.objects.filter(route_id=route_filter)
                query_routes = []
                for query_location in queryset:
                    for routes_filter_location in routes_filter_query:
                        if distance(routes_filter_location.location, query_location.location) < radius:
                            if routes_filter_location.route_id not in query_routes:
                                query_routes.append(query_location.route_id)
                query_routes.append(route_filter)
                query_routes = set(query_routes)
                friend_query = friend_query.filter(route_id__in=query_routes)
                queryset = queryset.filter(route_id__in=query_routes)
            '''

        if knn:
            if point:
                queryset = queryset.annotate(distance=func_Distance('location', point)).order_by('distance')
                friend_query = friend_query.annotate(distance=func_Distance('location', point)).order_by('distance')
            closest_routes = []
            for loc in queryset:
                if len(closest_routes) == knn:
                    break
                if loc.route_id not in closest_routes:
                    closest_routes.append(loc.route_id)

            queryset = queryset.filter(route_id__in=closest_routes).order_by('location_date')

            closest_routes = []
            for loc in friend_query:
                if len(closest_routes) == knn:
                    break
                if loc.route_id not in closest_routes:
                    closest_routes.append(loc.route_id)

            friend_query = friend_query.filter(route_id__in=closest_routes).order_by('location_date')

        return queryset | friend_query

    def _get_friend_query(self, friend_name):
        if friend_name:
            friend_queryset = Location.objects.filter(username=friend_name)
        else:
            friend_queryset = Location.objects.filter(username__in=[])
        return friend_queryset

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
    default_route_count = 10

    def get(self, request, *args, **kwargs):
        if request.user:
            if request.user.is_superuser:
                user_count = User.objects.count()
                point_count = Location.objects.filter(
                    is_active=True,
                    username__isnull=False,
                    route_id__isnull=False).count()
                route_list = list(set(Location.objects.values_list("route_id", flat=True)))
                route_count = len(route_list)
                user_list = User.objects.all()
            else:
                user_count = 1
                points = Location.objects.filter(
                    is_active=True,
                    route_id__isnull=False,
                    username=request.user.username)
                route_list = list(set(points.values_list("route_id", flat=True)))
                route_count = len(route_list)
                point_count = points.count()
                user_list = {}
            route_on_map = self.default_route_count if self.default_route_count < route_count else route_count
            friend_list = self._get_user_friends(request)

            return Response({"groups": json.dumps(self._group_by_route(route_list[:route_on_map])),
                             "route_on_map": route_on_map,
                             "user_count": user_count,
                             "point_count": point_count,
                             "route_count": route_count,
                             "friend_list": friend_list,
                             "user_list": user_list}, template_name="newfile.html")

        return Response({}, template_name="newfile.html")

    def _get_user_friends(self, request):
        if request.user.is_superuser:
            return User.objects.all().values_list("username", flat=True)
        return FriendList.objects.filter(friend_list__contains=[request.user.username]).values_list("username", flat=True) or []

    def _group_by_route(self, routes):
        groups = {}
        for route in routes:
            from rest_framework.renderers import JSONRenderer
            groups[route] = json.loads(JSONRenderer().render(LocationListSerializer(Location.objects.filter(route_id=route), many=True).data))

        return groups


class FriendListViewSet(generics.ListAPIView):
    template_name = "friend_list.html"
    renderer_classes = [TemplateHTMLRenderer]
    http_method_names = ['get', 'post']
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    default_route_count = 10

    def get(self, request, *args, **kwargs):
        try:
            f_list = FriendList.objects.get(username=request.user.username).friend_list
        except:
            f_list = []
        user_friends = self._get_user_friends(request)
        return Response({"friend_list": f_list, "user_friends": user_friends}, template_name="friend_list.html")

    def post(self, request, *args, **kwargs):
        try:
            username = request.POST['username']
        except:
            return self.get(request, args, **kwargs)

        try:
            f_list = FriendList.objects.get(username=request.user.username)
        except:
            f_list = FriendList.objects.create(username=request.user.username, friend_list=[])

        if username not in f_list.friend_list:
            f_list.friend_list.append(username)
        else:
            f_list.friend_list.remove(username)

        f_list.save()
        user_friends = self._get_user_friends(request)
        return Response({"friend_list": f_list.friend_list, "user_friends": user_friends}, template_name="friend_list.html")

    def _get_user_friends(self, request):
        return FriendList.objects.filter(friend_list__contains=[request.user.username]).values_list("username", flat=True) or []


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


def friend_list(request):
    if request.method == 'POST':
        try:
            f_list = FriendList.objects.get(username=request.user.username)
        except FriendList.DoesNotExist:
            f_list = FriendList.objects.create(username=request.user.username, friend_list=[])
        except Exception as e:
            print(e)
            return 400
        body_unicode = request.body.decode('utf-8')
        if body_unicode["username"] not in f_list.friend_list:
            f_list.friend_list.append(body_unicode["username"])
            return 200
        return 300
    if request.method == 'GET':
        try:
            f_list = FriendList.objects.get(username=request.user.username)
        except FriendList.DoesNotExist:
            f_list = FriendList.objects.create(username=request.user.username, friend_list=[])
        except Exception as e:
            print(e)
            return []
        return f_list.friend_list


class LocationBusyViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    ordering_fields = '__all__'
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user_filter = self.request.query_params.get('user_filter', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        friend_name = self.request.query_params.get('friend_name', None)
        friend_filter = False
        if friend_name:
            try:
                friend_list = FriendList.objects.get(username=self.request.user.username).friend_list
            except:
                friend_list = []

            if friend_name in friend_list:
                friend_filter = True

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
            if friend_name:
                friend_filter = True
            queryset = Location.objects.all()
            if user_filter:
                queryset = queryset.filter(username=user_filter)
            elif friend_filter:
                queryset = queryset.filter(username=friend_filter)
        else:
            queryset = Location.objects.filter(username=self.request.user.username)

        friend_query = self._get_friend_query(friend_name if friend_filter else False)

        if from_date is not None:
            try:
                from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
                queryset = queryset.filter(location_date__gte=from_date)
                friend_query = friend_query.filter(location_date__gte=from_date)
            except Exception as e:
                print(e)
                pass
        if to_date is not None:
            try:
                to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
                queryset = queryset.filter(location_date__lte=to_date)
                friend_query = friend_query.filter(location_date__lte=to_date)
            except Exception as e:
                print(e)
                pass
        if radius:
            if point:
                queryset = queryset.filter(location__distance_lt=(point, Distance(km=radius)))
                friend_query = friend_query.filter(location__distance_lt=(point, Distance(km=radius)))
        if knn:
            if point:
                queryset = queryset.annotate(distance=func_Distance('location', point)).order_by('distance')
                friend_query = friend_query.annotate(distance=func_Distance('location', point)).order_by('distance')

        return queryset | friend_query

    def _get_friend_query(self, friend_name):
        if friend_name:
            friend_queryset = Location.objects.filter(username=friend_name)
        else:
            friend_queryset = Location.objects.filter(username__in=[])
        return friend_queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LocationCreateSerializer

        return LocationListSerializer

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        date_range = self._get_busy_date(queryset)

        return Response({"data": queryset, "date_range": date_range})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        date_range = self._get_busy_date(queryset)
        from rest_framework.renderers import JSONRenderer
        queryset = json.loads(JSONRenderer().render(LocationListSerializer(queryset, many=True).data))

        return JsonResponse({"data": queryset, "date_range": date_range}, safe=True)

    def _get_busy_date(self, queryset):
        hour_multiplier = 2
        hour_to_add = datetime.timedelta(hours=hour_multiplier)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        # period = self.request.query_params.get('period', "7")
        key = "?"

        date_range_fiter = datetime.timedelta(days=int(50000))

        if from_date:
            try:
                from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            except Exception as e:
                print(e)
                return key
        if to_date:
            try:
                to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            except Exception as e:
                print(e)
                return key

        elif from_date:
            to_date = from_date + date_range_fiter

        start_hour = from_date.hour
        hour_counter = start_hour
        c_minute = from_date.minute
        from_date = from_date - datetime.timedelta(minutes=c_minute)
        c_minute = to_date.minute
        to_date = to_date - datetime.timedelta(minutes=c_minute)
        to_date = to_date + datetime.timedelta(hours=1)
        count = 0
        while from_date < to_date:
            tmp_count = queryset.filter(location_date__gte=from_date).filter(location_date__lte=from_date + hour_to_add).count()
            if tmp_count > count:
                count = tmp_count
                key = "{} {}:00 - {}:00".format(str(from_date.date()),
                                                hour_counter,
                                                ((hour_counter + 2) % 24))

            from_date = from_date + hour_to_add

        return {"key": key, "count": count}


class MapBusyViewSet(generics.ListAPIView):
    serializer_class = LocationListSerializer
    template_name = "map2.html"
    renderer_classes = [TemplateHTMLRenderer]
    http_method_names = ['get', 'post']
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    default_route_count = 10

    def get(self, request, *args, **kwargs):
        if request.user:
            if request.user.is_superuser:
                user_count = User.objects.count()
                points = Location.objects.filter(
                    is_active=True,
                    username__isnull=False,
                    route_id__isnull=False)
                point_count = points.count()
                user_list = User.objects.all()
            else:
                user_count = 1
                points = Location.objects.filter(
                    is_active=True,
                    route_id__isnull=False,
                    username=request.user.username)
                point_count = points.count()
                user_list = {}
            friend_list = self._get_user_friends(request)
            from rest_framework.renderers import JSONRenderer
            points = {"points": json.loads(JSONRenderer().render(LocationListSerializer(points, many=True).data))}

            points = json.dumps(points)

            return Response({"points": points,
                             "user_count": user_count,
                             "point_count": point_count,
                             "friend_list": friend_list,
                             "user_list": user_list}, template_name="density_map.html")

        return Response({}, template_name="newfile.html")

    def _get_user_friends(self, request):
        if request.user.is_superuser:
            return User.objects.all().values_list("username", flat=True)
        return FriendList.objects.filter(friend_list__contains=[request.user.username]).values_list("username", flat=True) or []


def get_user_route_count(request):
    point_count = 0
    route_count = 0

    if request.method == 'GET' and request.user:
        try:
            if request.user.is_superuser:
                locs = Location.objects.filter(is_active=True)
            else:
                locs = Location.objects.filter(username=request.user.username, is_active=True)
            route_count = len(set(locs.values_list("route_id", flat=True)))
            point_count = locs.count()
        except Exception as e:
            print(e)

    return JsonResponse({"point_count": point_count, "route_count": route_count})
