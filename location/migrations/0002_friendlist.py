# Generated by Django 3.1.3 on 2021-01-30 00:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('username', models.CharField(max_length=512, unique=True)),
                ('friend_list', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=512, unique=True), size=2048)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
