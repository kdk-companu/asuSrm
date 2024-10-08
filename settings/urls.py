from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from apps.workers.views import UserLogout, UserLogin, Workers
from apps.workers.views.error import error_noAccess_403, noAccessPage
from settings import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.workers.urls')),
    path('', include('apps.workobjects.urls')),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('', Workers.as_view(), name='index'),
    path('access/', noAccessPage.as_view(), name='access'),
    path("__debug__/", include("debug_toolbar.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
