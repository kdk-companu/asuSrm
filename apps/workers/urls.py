from django.urls import path

from apps.workers.views import Department_View, Department_Add, Department_Update, Subdivision_View, Chief_View, \
    Chief_Update, Subdivision_Update, Subdivision_Add, Chief_Add
from apps.workers.views.workers import Workers, Workers_Add, Workers_Filter, Workers_DetailView, Workers_Image, \
    Workers_Change_Password, User_Change, User_Basic_Change, User_Closed_Change, TEST, TEST2, TEST3, Workers_Passport, \
    Workers_Passport_Delete, Workers_Snils, Workers_Snils_Delete, Workers_Inn, Workers_Inn_Delete, Workers_Archive, \
    Workers_Archive_Delete, Workers_Signature, Workers_Signature_Delete

urlpatterns = [
    path('workers/', Workers.as_view(), name='workers'),
    path('workers/filter/', Workers_Filter.as_view(), name='workers_filter'),
    path('workers/add/', Workers_Add.as_view(), name='workers_add'),
    path('workers/<slug:workers_slug>/', Workers_DetailView.as_view(), name='workers_detail'),
    path('workers/<slug:workers_slug>/image/', Workers_Image.as_view(), name='workers_image'),
    path('workers/<slug:workers_slug>/passport/', Workers_Passport.as_view(), name='workers_passport'),
    path('workers/<slug:workers_slug>/passport/delete/', Workers_Passport_Delete.as_view(), name='workers_passport_delete'),
    path('workers/<slug:workers_slug>/snils/', Workers_Snils.as_view(), name='workers_snils'),
    path('workers/<slug:workers_slug>/snils/delete/', Workers_Snils_Delete.as_view(),
         name='workers_snils_delete'),
    path('workers/<slug:workers_slug>/inn/', Workers_Inn.as_view(), name='workers_inn'),
    path('workers/<slug:workers_slug>/inn/delete/', Workers_Inn_Delete.as_view(),
         name='workers_inn_delete'),
    path('workers/<slug:workers_slug>/archive/', Workers_Archive.as_view(), name='workers_archive'),
    path('workers/<slug:workers_slug>/archive/delete/', Workers_Archive_Delete.as_view(),
         name='workers_archive_delete'),

    path('workers/<slug:workers_slug>/signature/', Workers_Signature.as_view(),
         name='workers_signature'),
    path('workers/<slug:workers_slug>/signature/delete/', Workers_Signature_Delete.as_view(),
         name='workers_signature_delete'),


    path('workers/password/change/', Workers_Change_Password.as_view(), name='workers_change_password'),
    path('workers/<slug:workers_slug>/change/', User_Change.as_view(), name='workers_change'),
    path('workers/<slug:workers_slug>/change/basic/', User_Basic_Change.as_view(), name='workers_basic_change'),
    path('workers/<slug:workers_slug>/change/closed/', User_Closed_Change.as_view(), name='workers_closed_change'),




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



    path('test/', TEST.as_view(), name='test'),
    path('test2/<slug:workers_slug>/', TEST2.as_view(), name='test2'),
    path('test3/<slug:workers_slug>/', TEST3.as_view(), name='test3'),
]
