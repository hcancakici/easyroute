from django.contrib.gis.geos import Point

from rest_framework import serializers

from location.models import Location, LocationUser


class BaseModelSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)
    modified_date = serializers.DateTimeField(read_only=True)


class LocationUserSerializer(BaseModelSerializer):
    class Meta:
        model = LocationUser
        fields = '__all__'


class LocationSerializer(BaseModelSerializer):
    user = serializers.CharField()
    longitude = serializers.DecimalField(max_digits=19, decimal_places=10)
    latitude = serializers.DecimalField(max_digits=19, decimal_places=10)


    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'user')

    def create(self, validated_data):
        user = validated_data.pop('user')
        user, _ = LocationUser.objects.get_or_create(username=user)
        longitude = float(validated_data["longitude"])
        latitude = float(validated_data["latitude"])
        point = Point(longitude, latitude)
        validated_data["longitude"] = longitude
        validated_data["latitude"] = latitude
        point.srid = 4326
        location = Location.objects.create(user=user, location=point, **validated_data)
        return location
