import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brandsinfo.settings")
django.setup()  # Set up Django first

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

#  Now it's safe to import anything that touches models
from communications.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})



