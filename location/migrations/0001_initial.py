# Generated by Django 3.1.3 on 2021-01-17 14:54

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=11)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=11)),
                ('is_active', models.BooleanField(default=False)),
                ('location_date', models.DateTimeField(auto_now=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('username', models.CharField(max_length=512)),
                ('route_id', models.CharField(max_length=512)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
