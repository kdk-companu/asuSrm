from django.contrib import admin

# Register your models here.
from apps.workers.models import Department, Subdivision, Chief

admin.site.register(Subdivision)
admin.site.register(Department)
admin.site.register(Chief)