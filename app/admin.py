from django.contrib import admin

from .models import User, UserActivities

admin.site.register(User)
admin.site.register(UserActivities)
