from django.db import models
from django.contrib.gis.db import models as gismodels


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


class Location(BaseModel):
    latitude = models.DecimalField(max_digits=11, decimal_places=6)
    longitude = models.DecimalField(max_digits=11, decimal_places=6)
    is_active = models.BooleanField(default=False)
    location_date = models.DateTimeField(auto_now=True)
    location = gismodels.PointField(null=True, blank=True, geography=False)
    username = models.CharField(max_length=512)
    route_id = models.CharField(max_length=512)