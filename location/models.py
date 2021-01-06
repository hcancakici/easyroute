from django.db import models
from django.contrib.gis.db import models as gismodels


# Create your models here.

def get_sentinel_user():
    return LocationUser.objects.get_or_create(username='deleted')[0]


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields', None)
        if update_fields is not None:
            update_fields.append('modified_date')
        super(BaseModel, self).save(*args, **kwargs)


class LocationUser(BaseModel):
    username = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.username


class Location(BaseModel):
    latitude = models.DecimalField(max_digits=11, decimal_places=6)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    location_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(LocationUser, on_delete=models.SET(get_sentinel_user))
    location = gismodels.PointField(null=True, blank=True)
