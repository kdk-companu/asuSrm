from django.urls import path

# from apps.workers.views import Department_View, Department_Add, Department_Update, Subdivision_View, Chief_View, \
#     Chief_Update, Subdivision_Update, Subdivision_Add, Chief_Add
# from apps.workers.views.workers import Workers, Workers_Add, Workers_Filter, Workers_DetailView, Workers_Image, \
#     Workers_Change_Password, User_Change, User_Basic_Change, User_Closed_Change, Workers_Passport, \
#     Workers_Passport_Delete, Workers_Snils, Workers_Snils_Delete, Workers_Inn, Workers_Inn_Delete, Workers_Archive, \
#     Workers_Archive_Delete, Workers_Signature, Workers_Signature_Delete, Workers_Update_Password, Group_Permissions, \
#     User_Permissions
from apps.workers.views import Subdivision_View, Subdivision_Add, Subdivision_Update, Department_View, Department_Add, \
    Department_Update, Chief_View, Chief_Add, Chief_Update, Workers, Group_Permissions, Workers_Filter, Workers_Add, \
    Workers_DetailView, Workers_Image, User_Permissions, Workers_Update_Password, Workers_Change_Password, \
    Workers_Change, WorkerBasic_Change, WorkerClosed_Change, WorkerClosed_Passport, WorkerClosed_Passport_Delete, \
    WorkerClosed_Snils, WorkerClosed_Snils_Delete, WorkerClosed_Inn, WorkerClosed_Inn_Delete, WorkerClosed_Archive, \
    WorkerClosed_Archive_Delete, WorkerClosed_Signature, WorkerClosed_Signature_Delete

urlpatterns = [
    path('workers/', Workers.as_view(), name='workers'),
    path('workers/filter/', Workers_Filter.as_view(), name='workers_filter'),
    path('workers/add/', Workers_Add.as_view(), name='workers_add'),
    path('workers/<slug:workers_slug>/', Workers_DetailView.as_view(), name='workers_detail'),
    path('workers/<slug:workers_slug>/image/', Workers_Image.as_view(), name='workers_image'),
    path('workers/<slug:workers_slug>/passport/', WorkerClosed_Passport.as_view(), name='workers_passport'),
    path('workers/<slug:workers_slug>/passport/delete/', WorkerClosed_Passport_Delete.as_view(),
         name='workers_passport_delete'),
    path('workers/<slug:workers_slug>/snils/', WorkerClosed_Snils.as_view(), name='workers_snils'),
    path('workers/<slug:workers_slug>/snils/delete/', WorkerClosed_Snils_Delete.as_view(),
         name='workers_snils_delete'),
    path('workers/<slug:workers_slug>/inn/', WorkerClosed_Inn.as_view(), name='workers_inn'),
    path('workers/<slug:workers_slug>/inn/delete/', WorkerClosed_Inn_Delete.as_view(),
         name='workers_inn_delete'),
    path('workers/<slug:workers_slug>/archive/', WorkerClosed_Archive.as_view(), name='workers_archive'),
    path('workers/<slug:workers_slug>/archive/delete/', WorkerClosed_Archive_Delete.as_view(),
         name='workers_archive_delete'),
    path('workers/<slug:workers_slug>/signature/', WorkerClosed_Signature.as_view(),
         name='workers_signature'),
    path('workers/<slug:workers_slug>/signature/delete/', WorkerClosed_Signature_Delete.as_view(),
         name='workers_signature_delete'),
    path('workers/password/change/', Workers_Change_Password.as_view(), name='workers_change_password'),
    path('workers/<slug:workers_slug>/password/update/', Workers_Update_Password.as_view(),
         name='workers_update_password'),
    path('workers/<slug:workers_slug>/change/', Workers_Change.as_view(), name='workers_change'),
    path('workers/<slug:workers_slug>/change/basic/', WorkerBasic_Change.as_view(), name='workers_basic_change'),
    path('workers/<slug:workers_slug>/change/closed/', WorkerClosed_Change.as_view(), name='workers_closed_change'),
    path('workers/<slug:workers_slug>/permissions/', User_Permissions.as_view(), name='workers_permissions'),
    #
    path('workers/settings/subdivision/', Subdivision_View.as_view(), name='subdivision'),
    path('workers/settings/subdivision/add/', Subdivision_Add.as_view(), name='subdivision_add'),
    path('workers/settings/subdivision/update/<slug:subdivision_slug>', Subdivision_Update.as_view(),
         name='subdivision_update'),
    path('workers/settings/department/', Department_View.as_view(), name='department'),
    path('workers/settings/department/add/', Department_Add.as_view(), name='department_add'),
    path('workers/settings/department/update/<slug:department_slug>', Department_Update.as_view(),
         name='department_update'),
    path('workers/settings/chief/', Chief_View.as_view(), name='chief'),
    path('workers/settings/chief/add/', Chief_Add.as_view(), name='chief_add'),
    path('workers/settings/chief/update/<slug:chief_slug>', Chief_Update.as_view(),
         name='chief_update'),
    path('workers/settings/chief/<int:pk>/permissions/', Group_Permissions.as_view(),
         name='chief_permissions'),

]
