
from django.contrib import admin
from django.urls import path,include
import usershome.urls
import bAdmin.urls
import communications.urls 
from django.conf.urls.static import static
from . import settings
from . import mapper
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/',include(usershome.urls)),
    path('badmin/',include(bAdmin.urls)),
    path('communications/',include(communications.urls)),
    path('mapper/<int:maping_id>/',mapper.mapper_view),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
