
from django.contrib import admin
from django.urls import path,include
import usershome.urls
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
    path('mapper/<int:maping_id>/',mapper.mapper_view),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]


from django.urls import re_path
from .websocket_consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
