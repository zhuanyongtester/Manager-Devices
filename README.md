webSocket 终于调通，看了网上好多的视频，都不详细解决，一直有问题
1、检查相关版本我的版本如下，安装以上3三方包：
channels==4.2.0
channels_redis==4.2.1
daphne==4.1.2
Django==5.1.4
redis==5.2.1
2、注册模块都是在根目录的setting
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    ....
    ....
    'channels'
]
3.配置setting wsgi,这里之前默认走的wsgi，我现在改成asgi
ASGI_APPLICATION='HuaweiDevicesManager.asgi.application' #HuaweiDevicesManager 换成你项目名字
4.配置redis 服务器连接配置 也是在setting里
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6380)],  # Redis 地址
        },
    },
}
这里注意我的redis服务端在windows启动，我其他版本都比较高，这个redis在网上window版本只有3.0的，然后后面调测会报错，
我在网上找到5.x的在media-redis下的reids-windows-5x.zip，然后解压启动reids-sever
5.在根目录下asgi.py配置这个：
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
然后配置你的routing：

from django.urls import path

from apps.CustomManager.consumers import DeviceConsumer

websocket_urlpatterns = [
    path('api/ws/device/<device_id>/', DeviceConsumer.as_asgi()),  # 更新为匹配设备 ID
]
6.配置DeviceConsumer
# consumers.py
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from django.utils.timezone import now

from apps.CustomManager.asgi import django_application
from apps.CustomManager.models import TempQrSession


class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        device_id = self.scope['url_route']['kwargs']['device_id']
        self.device_id = device_id
        await self.accept()  # 确保连接成功后再继续


    async def receive(self, text_data):
        # 处理客户端发来的消息
        data = json.loads(text_data)

        # 在这里你可以根据实际需求进行消息的处理，例如：
        # - 执行某些操作
        # - 推送消息到设备等

        # 示例：你可以检查是否有需要通知的内容


    async def disconnect(self, close_code):
        # 设备断开连接
        print(f"Device {self.device_id} disconnected.")

        # 清理资源等操作
        # 例如：关闭 WebSocket 连接等
        await self.close()

6.调测我用postman模拟
![image](https://github.com/user-attachments/assets/46ebfc50-9e72-4cc4-b18e-548c54ce0b90)
服务端收到
HTTP GET /api/gen 200 [0.02, 127.0.0.1:52894]
WebSocket HANDSHAKING /api/ws/device/7c4a175a-cfa6-44b1-a6ef-236ab97c0eec/ [127.0.0.1:52921]
WebSocket CONNECT /api/ws/device/7c4a175a-cfa6-44b1-a6ef-236ab97c0eec/ [127.0.0.1:52921]
Device 7c4a175a-cfa6-44b1-a6ef-236ab97c0eec connected successfully.
Device 7c4a175a-cfa6-44b1-a6ef-236ab97c0eec connected and verified.

7.不要忘记别服务器windows启动redeis
![image](https://github.com/user-attachments/assets/23119ab7-f39c-49f7-a2dd-8852cd635e2d)


