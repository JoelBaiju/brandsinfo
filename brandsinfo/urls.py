
from django.contrib import admin
from django.urls import path,include
import usershome.urls
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/',include(usershome.urls))
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
