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
        print(f"Device {self.device_id} connected successfully.")

        # 然后进行其他逻辑，如验证 session_id 或 token
        if not self.device_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Session ID missing'
            }))
            await self.close()
            return

        user = await self.verify_token(self.device_id)
        if not user:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid or expired token'
            }))
            await self.close()
            return

        # 如果验证通过，发送连接成功信息
        await self.send(text_data=json.dumps({
            'type': 'waiting',
            'message': 'Please scan the QR code to log in.',
        }))
        self.user = user
        self.device_id = self.device_id
        print(f"Device {self.device_id} connected and verified.")

    async def receive(self, text_data):
        # 处理客户端发来的消息
        data = json.loads(text_data)

        # 在这里你可以根据实际需求进行消息的处理，例如：
        # - 执行某些操作
        # - 推送消息到设备等

        # 示例：你可以检查是否有需要通知的内容
        if data.get('action') == 'check_login':
            if self.user and self.token:
                if not self.is_token_expired(self.token):
                    await self.send(text_data=json.dumps({
                        'type': 'login_status',
                        'message': 'You can login now.',
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Token expired, please re-login.',
                    }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Session or user not valid.',
                }))
        # 其他操作...

    async def disconnect(self, close_code):
        # 设备断开连接
        print(f"Device {self.device_id} disconnected.")

        # 清理资源等操作
        # 例如：关闭 WebSocket 连接等
        await self.close()

    async def verify_token(self, session_id):
        """验证 Token 是否有效（可以根据你的实际需求来修改）"""
        if not session_id:
            return None

        # 例如，检查 token 是否存在并且有效
        # 假设你有一个 UserProfile 模型存储 token 和用户信息
        try:
            user = await database_sync_to_async(TempQrSession.objects.get)(session_key=session_id)
            if user:
                # 如果 token 没有过期，返回用户信息
                if user.expires_at<=now():
                    return None  # 如果 token 过期，则返回 None
                if not user.is_active:
                    return None
                return user
        except TempQrSession.DoesNotExist:
            return None

