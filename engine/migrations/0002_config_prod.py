# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-29 09:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='prod',
            field=models.BooleanField(default=False),
        ),
    ]
