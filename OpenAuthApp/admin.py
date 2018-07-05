from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.admin import site

from models import *

import os

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
