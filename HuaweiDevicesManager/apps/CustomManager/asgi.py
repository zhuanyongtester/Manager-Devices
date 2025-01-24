import os

from django.core.asgi import get_asgi_application

# 注意修改项目名
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django3_websocket.settings')

django_application = get_asgi_application()


async def application(scope, receive, send):
    if scope['type'] == 'http':
        # Let Django handle HTTP requests
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        # We'll handle Websocket connections here
        pass
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")