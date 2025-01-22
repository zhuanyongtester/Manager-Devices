
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.CustomManager import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HuaweiDevicesManager.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(routing.websocket_urlpatterns)  # 确保这里引用了正确的路由
    ),
})