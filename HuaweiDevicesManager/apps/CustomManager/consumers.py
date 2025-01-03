from channels.generic.websocket import AsyncWebsocketConsumer
import json


class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 获取 WebSocket 连接的参数
        self.device_id = self.scope['url_route']['kwargs']['session_id']
        print(f"Device ID: {self.device_id}")

        self.room_group_name = f"device_{self.device_id}"
        if not self.device_id:
            # 如果没有 device_id，拒绝连接
            await self.close()
            return
        print(f"Device ID: {self.device_id}")

        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 允许 WebSocket 连接
        await self.accept()

    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # 从客户端接收到的消息
        data = json.loads(text_data)
        message = data.get("message")

        # 发送消息给房间组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'device_message',
                'message': message
            }
        )

    async def device_message(self, event):
        # 将消息发送给 WebSocket 客户端
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
