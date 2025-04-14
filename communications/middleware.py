from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from jwt.exceptions import InvalidTokenError, DecodeError
from django.db import close_old_connections


@database_sync_to_async
def get_user_from_token(token):
    try:
        validated_token = UntypedToken(token)
        return JWTAuthentication().get_user(validated_token)
    except (InvalidTokenError, DecodeError):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")
        print('from ws auth middleware')
        if token:
            scope["user"] = await get_user_from_token(token[0])
        else:
            scope["user"] = AnonymousUser()

        close_old_connections()
        return await super().__call__(scope, receive, send)
