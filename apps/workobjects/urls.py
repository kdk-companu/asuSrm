from django.urls import path

from apps.workobjects.views import OrganizationsObjects_View, OrganizationsObjects_Add, OrganizationsObjects_Update

urlpatterns = [
    path('objects/', OrganizationsObjects_View.as_view(), name='objects'),
    path('objects/add', OrganizationsObjects_Add.as_view(), name='objects_add'),
    path('objects/update/<slug:objects_slug>', OrganizationsObjects_Update.as_view(), name='objects_update'),
]
