# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-29 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0005_businessuser_ituser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logs_B',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', models.TextField(blank=True, null=True)),
                ('icici_user_id', models.TextField(blank=True, null=True)),
                ('query', models.TextField(blank=True, null=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('chatbot_answer', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Logs_IT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alexa_id', models.TextField(blank=True, null=True)),
                ('device_id', models.TextField(blank=True, null=True)),
                ('access_token', models.TextField(blank=True, null=True)),
                ('query', models.TextField(blank=True, null=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('chatbot_answer', models.TextField(blank=True, null=True)),
                ('icici_user_id', models.TextField(blank=True, null=True)),
                ('request_packets_fired', models.TextField(blank=True, null=True)),
                ('response_packets_fired', models.TextField(blank=True, null=True)),
                ('latency', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
