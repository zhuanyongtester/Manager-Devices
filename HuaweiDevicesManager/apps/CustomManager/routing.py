# CustomerManager/routing.py
from django.urls import re_path
from .consumers import DeviceConsumer

websocket_urlpatterns = [
    re_path(r'^device/(?P<device_id>[a-f0-9\-]+)/$', DeviceConsumer.as_asgi()),  # 提取 device_id

]
