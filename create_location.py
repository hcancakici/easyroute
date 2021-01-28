from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
import datetime

from location.models import Location
from random import randint

import json


def create_location():
    names = {"fatih": 0, "faruk": 0, "can": 0, "merve": 0, "derya": 0, "maziyar": 0, "anil": 0, "sami": 0, "kaan": 0, "melisa": 0, "dilek": 0}
    try:
        for name in names:
            user = User.objects.create(username=name, password=name)
            user.set_password(name)
            user.save()
    except:
        pass
    try:
        i = 0
        while True:
            i += 1
            with open('lokasyonlar/loc_data_{}.txt'.format(str(i)), 'r') as filehandle:
                random_user = randint(0, 10)
                name = list(names)
                name = name[random_user]
                names[name] += 1
                route_id = "{}_{}".format(name, str(names[name]))
                random_day = randint(3, 13)
                random_hour = randint(10, 16)
                my_date = datetime.datetime.now()
                my_date = my_date.replace(hour=random_hour)
                my_date = my_date.replace(day=random_day)
                print(my_date)
                locations = json.load(filehandle)
                seconds = 15

                for location in locations:
                    lat, lon = location.split(",")
                    lat = float(lat)
                    lon = float(lon)
                    point = Point(lon, lat)
                    point.srid = 4326
                    lo = Location.objects.create(
                        username=name,
                        location=point,
                        latitude=lat,
                        longitude=lon,
                        route_id=route_id,
                        is_active=True,
                        location_date=my_date
                    )
                    lo = Location.objects.filter(id=lo.id)
                    lo.update(location_date=my_date)
                    my_date = my_date + datetime.timedelta(seconds=seconds)
    except Exception as e:
        print(e)
