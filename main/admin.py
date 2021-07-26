from django.contrib import admin
from .models import PIoT, SoftwareGroup

admin.site.site_url = 'https://hive-bind.net/dashboard/'
admin.site.register(PIoT)
admin.site.register(SoftwareGroup)
