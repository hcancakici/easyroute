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
    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'user')

    def create(self, validated_data):
        user = validated_data.pop('user')
        user, _ = LocationUser.objects.get_or_create(username=user)
        location = Location.objects.create(user=user,**validated_data)
        return location
