from channels import routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from apps.CustomManager import consumers
from apps.CustomManager.consumers import DeviceConsumer

websocket_urlpatterns = [
    path('api/ws/device/<device_id>/', DeviceConsumer.as_asgi()),  # 更新为匹配设备 ID
]

