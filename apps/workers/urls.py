from django.urls import path

from apps.workers.views import Subdivision_View, Subdivision_Add, Subdivision_Update, Department_View, Department_Add, \
    Department_Update, Chief_View, Chief_Add, Chief_Update, Workers, Group_Permissions, Workers_Filter, Workers_Add, \
    Workers_DetailView, Workers_Image, User_Permissions, Workers_Update_Password, Workers_Change_Password, \
    Workers_Change, WorkerBasic_Change, WorkerClosed_Change, WorkerClosed_Passport, WorkerClosed_Passport_Delete, \
    WorkerClosed_Snils, WorkerClosed_Snils_Delete, WorkerClosed_Inn, WorkerClosed_Inn_Delete, WorkerClosed_Archive, \
    WorkerClosed_Archive_Delete, WorkerClosed_Signature, WorkerClosed_Signature_Delete, OrganizationExploitation_View, \
    OrganizationExploitation_Update, OrganizationExploitation_Add

from apps.workers.views.user_worker_planning import InformationMissing_View, InformationMissing_Add, \
    Workers_Work_Planning_View, InformationMissing_Update, InformationWeekendsHolidays_View, \
    InformationWeekendsHolidays_Add, InformationWeekendsHolidays_Update, WorkersMissing_View, WorkersMissing_Add, \
    WorkersMissing_Update, WorkersWeekendWork_Update, WorkersWeekendWork_Add, WorkersWeekendWork_View, \
    WorkersWeekendWork_Time_Update, WorkersMission_View, WorkersMission_Add, WorkersMission_Update, \
    Workers_Work_Planning_Subdivision_View, Workers_Work_Planning_Department_View, WorkersMissing_UserHis_View, \
    WorkersMissing_UserHis_Add, WorkersMissing_UserHis_Update, WorkersMissing_Department_View, \
    WorkersMissing_Subdivision_View, WorkersMissing_Subdivision_Add, WorkersMissing_Department_Add, \
    WorkersMissing_Subdivision_Update, WorkersMissing_Department_Update

urlpatterns = [
    path('user/workers/subdivision/', Subdivision_View.as_view(), name='subdivision'),
    path('user/workers/subdivision/add/', Subdivision_Add.as_view(), name='subdivision_add'),
    path('user/workers/subdivision/update/<slug:subdivision_slug>', Subdivision_Update.as_view(),
         name='subdivision_update'),
    path('user/workers/department/', Department_View.as_view(), name='department'),
    path('user/workers/department/add/', Department_Add.as_view(), name='department_add'),
    path('user/workers/department/update/<slug:department_slug>', Department_Update.as_view(),
         name='department_update'),
    path('user/workers/chief/', Chief_View.as_view(), name='chief'),
    path('user/workers/chief/add/', Chief_Add.as_view(), name='chief_add'),
    path('user/workers/chief/update/<slug:chief_slug>', Chief_Update.as_view(),
         name='chief_update'),
    path('user/workers/chief/<int:pk>/permissions/', Group_Permissions.as_view(), name='chief_permissions'),

    path('user/workers/planning/', Workers_Work_Planning_View.as_view(),
         name='workers_planning'),



    path('user/workers/', Workers.as_view(), name='workers'),
    path('user/workers/filter/', Workers_Filter.as_view(), name='workers_filter'),
    path('user/workers/add/', Workers_Add.as_view(), name='workers_add'),
    path('user/workers/password/change/', Workers_Change_Password.as_view(), name='workers_change_password'),
    path('user/workers/<slug:workers_slug>/', Workers_DetailView.as_view(), name='workers_detail'),
    path('user/workers/<slug:workers_slug>/change/', Workers_Change.as_view(), name='workers_change'),
    path('user/workers/<slug:workers_slug>/change/permissions/', User_Permissions.as_view(),
         name='workers_permissions'),
    path('user/workers/<slug:workers_slug>/change/image/', Workers_Image.as_view(), name='workers_image'),
    path('user/workers/<slug:workers_slug>/password/update/', Workers_Update_Password.as_view(),
         name='workers_update_password'),
    path('user/workers/<slug:workers_slug>/change/basic/', WorkerBasic_Change.as_view(), name='workers_basic_change'),
    path('user/workers/<slug:workers_slug>/change/closed/', WorkerClosed_Change.as_view(),
         name='workers_closed_change'),
    path('user/workers/<slug:workers_slug>/passport/change/', WorkerClosed_Passport.as_view(), name='workers_passport'),
    path('user/workers/<slug:workers_slug>/passport/delete/', WorkerClosed_Passport_Delete.as_view(),
         name='workers_passport_delete'),
    path('user/workers/<slug:workers_slug>/snils/change/', WorkerClosed_Snils.as_view(), name='workers_snils'),
    path('user/workers/<slug:workers_slug>/snils/delete/', WorkerClosed_Snils_Delete.as_view(),
         name='workers_snils_delete'),
    path('user/workers/<slug:workers_slug>/inn/change/', WorkerClosed_Inn.as_view(), name='workers_inn'),
    path('user/workers/<slug:workers_slug>/inn/delete/', WorkerClosed_Inn_Delete.as_view(),
         name='workers_inn_delete'),
    path('user/workers/<slug:workers_slug>/archive/change/', WorkerClosed_Archive.as_view(), name='workers_archive'),
    path('user/workers/<slug:workers_slug>/archive/delete/', WorkerClosed_Archive_Delete.as_view(),
         name='workers_archive_delete'),
    path('user/workers/<slug:workers_slug>/signature/change/', WorkerClosed_Signature.as_view(),
         name='workers_signature'),
    path('user/workers/<slug:workers_slug>/signature/delete/', WorkerClosed_Signature_Delete.as_view(),
         name='workers_signature_delete'),








    path('user/exploitations/organizations/', OrganizationExploitation_View.as_view(), name='organizationExploitation'),
    path('user/exploitations/organizations/update/<slug:organizationExploitation_slug>',
         OrganizationExploitation_Update.as_view(), name='organizationExploitation_update'),
    path('user/exploitations/organizations/add', OrganizationExploitation_Add.as_view(),
         name='organizationExploitation_add'),



    path('user/workers/planning/missing/', WorkersMissing_View.as_view(),
         name='workers_missing'),
    path('user/workers/planning/<slug:subdivision_slug>/missing/', WorkersMissing_Subdivision_View.as_view(),
         name='workers_missing_subdivision'),
    path('user/workers/planning/<slug:subdivision_slug>/<slug:department_slug>/missing/', WorkersMissing_Department_View.as_view(),
         name='workers_missing_subdivision_department'),

    path('user/workers/planning/missing/add/', WorkersMissing_Add.as_view(),
         name='workers_missing_add'),
    path('user/workers/planning/missing/<slug:subdivision_slug>/add', WorkersMissing_Subdivision_Add.as_view(),
         name='workers_missing_subdivision_add'),
    path('user/workers/planning/<slug:subdivision_slug>/<slug:department_slug>/missing/add',
         WorkersMissing_Department_Add.as_view(),
         name='workers_missing_subdivision_department_add'),

    path('user/workers/planning/missing/update/<int:pk>', WorkersMissing_Update.as_view(),
         name='workers_missing_update'),
    path('user/workers/planning/missing/<slug:subdivision_slug>/update/<int:pk>', WorkersMissing_Subdivision_Update.as_view(),
         name='workers_missing_subdivision_update'),
    path('user/workers/planning/<slug:subdivision_slug>/<slug:department_slug>/missing/update/<int:pk>',
         WorkersMissing_Department_Update.as_view(),
         name='workers_missing_subdivision_department_update'),

    path('user/workers/<slug:workers_slug>/missing/', WorkersMissing_UserHis_View.as_view(),
         name='workers_missing_userHis'),
    path('user/workers/<slug:workers_slug>/missing/add/', WorkersMissing_UserHis_Add.as_view(),
         name='workers_missing_userHis_add'),
    path('user/workers/<slug:workers_slug>/missing/update/<int:pk>', WorkersMissing_UserHis_Update.as_view(),
         name='workers_missing_userHis_update'),




    path('user/workers/planning/<slug:subdivision_slug>', Workers_Work_Planning_Subdivision_View.as_view(),
         name='workers_planning_subdivision'),
    path('user/workers/planning/<slug:subdivision_slug>/<slug:department_slug>', Workers_Work_Planning_Department_View.as_view(),
         name='workers_planning_subdivision_department'),


    path('workers/planning/weekendwork/', WorkersWeekendWork_View.as_view(),
         name='workers_weekendwork'),
    path('workers/planning/weekendwork/add/', WorkersWeekendWork_Add.as_view(),
         name='workers_weekendwork_add'),
    path('workers/planning/weekendwork/update/<int:pk>', WorkersWeekendWork_Update.as_view(),
         name='workers_weekendwork_update'),
    path('workers/planning/weekendwork/update/time/<int:pk>', WorkersWeekendWork_Time_Update.as_view(),
         name='workers_weekendwork_time_update'),

    path('user/workers/planning/mission/', WorkersMission_View.as_view(),
         name='workersMission'),
    path('user/workers/planning/mission/add/', WorkersMission_Add.as_view(),
         name='workersMission_add'),
    path('user/workers/planning/mission/update/<int:pk>', WorkersMission_Update.as_view(),
         name='workersMission_update'),

    #
    path('user/workers/planning/informationmissing/', InformationMissing_View.as_view(), name='informationmissing'),
    path('user/workers/planning/informationmissing/add/', InformationMissing_Add.as_view(), name='informationmissing_add'),
    path('user/workers/planning/informationmissing/update/<slug:informationmissing_slug>',
         InformationMissing_Update.as_view(),
         name='informationmissing_update'),
    path('user/workers/planning/informationweekendsholidays/', InformationWeekendsHolidays_View.as_view(),
         name='informationweekendsholidays'),
    path('user/workers/planning/informationweekendsholidays/add/', InformationWeekendsHolidays_Add.as_view(),
         name='informationweekendsholidays_add'),
    path('user/workers/planning/informationweekendsholidays/update/<int:pk>/',
         InformationWeekendsHolidays_Update.as_view(), name='informationweekendsholidays_update'),

    #


]
