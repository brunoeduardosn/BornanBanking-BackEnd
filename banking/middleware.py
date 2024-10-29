from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken

User = get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        UntypedToken(token)
        return User.objects.get(token=token)
    except (User.DoesNotExist, InvalidToken):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from the query string
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")

        # Authenticate the user
        scope['user'] = await get_user(token[0]) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)
