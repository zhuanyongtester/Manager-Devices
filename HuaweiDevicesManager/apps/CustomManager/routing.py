
from django.urls import path,re_path
from apps.CustomManager.consumers import QrCodeConsumer


websocket_urlpatterns=[
    path('ws/', QrCodeConsumer.as_asgi()),
]