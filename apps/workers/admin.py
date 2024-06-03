from django.contrib import admin
from apps.workers.models import UserBasic, Worker, Watcher, Serviceman, Customer, Exploitation, WorkerBasic, \
    Subdivision, Department, Chief, WorkerClosed, InformationMissing, InformationWeekendsHolidays, WorkersMissing, \
 WorkersWeekendWork

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


admin.site.register(InformationMissing)
admin.site.register(InformationWeekendsHolidays)
admin.site.register(WorkersMissing)
admin.site.register(WorkersWeekendWork)
