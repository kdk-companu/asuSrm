from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

# from apps.workers.models import Department, Subdivision, Chief, User, Organization, Organization_Direction, User_Basic, \
#     User_Closed, UserType1, UserType2
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from apps.workers.models import UserBasic, Worker, Watcher, Serviceman, Customer, Exploitation, WorkerBasic, \
    Subdivision, Department, Chief, WorkerClosed


admin.site.register(UserBasic)
admin.site.register(Worker)
admin.site.register(WorkerBasic)
admin.site.register(WorkerClosed)
admin.site.register(Watcher)
admin.site.register(Exploitation)
admin.site.register(Customer)
admin.site.register(Serviceman)

admin.site.register(Subdivision)
admin.site.register(Department)
admin.site.register(Chief)
