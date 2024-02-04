from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from apps.workers.views import Workers_Login, Workers_Logout
from settings import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.workers.urls')),
    path('login/', Workers_Login.as_view(), name='login'),
    path('logout/', Workers_Logout.as_view(), name='logout'),



    path("__debug__/", include("debug_toolbar.urls")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
