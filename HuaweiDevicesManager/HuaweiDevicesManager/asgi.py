"""
ASGI config for HuaweiDevicesManager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from apps.CustomManager import urls as device_urls  # 引用刚才定义的 websocket_urlpatterns



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HuaweiDevicesManager.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # 在这里添加你的 WebSocket 路由
                URLRouter(device_urls.websocket_urlpatterns),  # 使用 websocket_urlpatterns

            ])
        )
    ),
})
