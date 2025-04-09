# asgi.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import communications.routing  # keep WebSocket stuff here


application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # serve normal HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(communications.routing.websocket_urlpatterns)
    ),
})
