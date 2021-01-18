from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

from rest_framework import serializers

from location.models import Location


class BaseModelSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)
    modified_date = serializers.DateTimeField(read_only=True)


class LocationCreateSerializer(BaseModelSerializer):
    route_id = serializers.CharField()
    is_active = serializers.BooleanField()
    longitude = serializers.DecimalField(max_digits=19, decimal_places=10)
    latitude = serializers.DecimalField(max_digits=19, decimal_places=10)

    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'is_active', 'route_id')

    def create(self, validated_data):
        '''
            username,
            route_id,
            longitude,
            latitude,
            is_active
        '''
        longitude = float(validated_data["longitude"])
        latitude = float(validated_data["latitude"])
        is_active = validated_data["is_active"]
        try:
            username = self.context['request'].user.username
        except:
            raise serializers.ValidationError("Invalid user")

        validated_data["username"] = username

        point = Point(longitude, latitude)
        validated_data["longitude"] = longitude
        validated_data["latitude"] = latitude
        point.srid = 4326
        location = Location.objects.create(location=point, **validated_data)
        if is_active:
            Location.objects.filter(route_id=location.route_id).update(is_active=True)

        return location


class LocationListSerializer(BaseModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
