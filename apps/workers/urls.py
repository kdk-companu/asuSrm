from django.urls import path

from apps.workers.views import Department_View, Department_Add, Department_Update, Subdivision_View, Chief_View, \
    Chief_Update, Subdivision_Update, Subdivision_Add, Chief_Add
from apps.workers.views.workers import Workers, Workers_Add, Workers_Filter, Workers_DetailView

urlpatterns = [
    path('workers/', Workers.as_view(), name='workers'),
    path('workers/filter/', Workers_Filter.as_view(), name='workers_filter'),
    path('workers/add/', Workers_Add.as_view(), name='workers_add'),
    path('workers/<slug:workers_slug>/', Workers_DetailView.as_view(), name='workers_detail'),



    path('workers/settings/subdivision/', Subdivision_View.as_view(), name='subdivision'),
    path('workers/settings/subdivision/add/', Subdivision_Add.as_view(), name='subdivision_add'),
    path('workers/settings/subdivision/update/<slug:subdivision_slug>', Subdivision_Update.as_view(), name='subdivision_update'),

    path('workers/settings/department/', Department_View.as_view(), name='department'),
    path('workers/settings/department/add/', Department_Add.as_view(), name='department_add'),
    path('workers/settings/department/update/<slug:department_slug>', Department_Update.as_view(),
         name='department_update'),

    path('workers/settings/chief/', Chief_View.as_view(), name='chief'),
    path('workers/settings/chief/add/', Chief_Add.as_view(), name='chief_add'),
    path('workers/settings/chief/update/<slug:chief_slug>', Chief_Update.as_view(),
         name='chief_update'),
    ]