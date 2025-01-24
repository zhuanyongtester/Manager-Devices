from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now
from datetime import timedelta
import json
from urllib.parse import parse_qs
import asyncio

from apps.CustomManager.accountManger.WebsocketParm import WebsocketParm
from apps.CustomManager.models import TempQrSession, UserProfile


class DeviceConsumer(AsyncWebsocketConsumer, WebsocketParm):
    def __init__(self):
        super().__init__()
        self.role_gen = "Gener"  # 设备 A (生成器)
        self.role_scaner = "Scaner"  # 设备 B (扫描器)
        self.status_waiting = 'waiting'
        self.status_approved = 'approved'
        self.status_rejected = 'rejected'
        self.status_timeout = 'timeout'
        self.timer_task = None  # 定时器任务引用

    async def connect(self):
        try:
            # 从 URL 和查询参数中提取信息
            self.session_id = self.scope['url_route']['kwargs'].get('device_id', None)
            query_params = parse_qs(self.scope['query_string'].decode())
            self.role = query_params.get('role', [None])[0]
            self.access_token = query_params.get('access_token', [None])[0]
            self.group_name = f"group_{self.session_id}"

            # 校验 session_id 是否存在
            if not self.session_id:
                await self.send(json.dumps({"statusCode": 400, "message": "Missing session_id"}))
                await self.close()
                return

            # 加入 WebSocket 群组
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # 根据角色处理不同逻辑
            if self.role == self.role_gen:
                await self.handle_device_a_connection()
            elif self.role == self.role_scaner:
                await self.handle_device_b_connection()
            else:
                await self.send(json.dumps({"statusCode": 400, "message": "Unknown role"}))
                await self.close()

        except Exception as e:
            await self.send(json.dumps({"statusCode": 500, "message": f"Error during connection: {str(e)}"}))
            await self.close()

    async def handle_device_a_connection(self):
        """处理设备 A 的连接逻辑"""
        try:
            is_valid = await self.is_valid_session(self.session_id)
            if not is_valid:
                await self.send(json.dumps({
                    "statusCode": 400,
                    "message": "Invalid or expired session_id"
                }))
                await self.close()
                return

            # 设置 30 秒超时定时器
            self.timer_task = asyncio.create_task(self.close_after_timeout(30))
            await self.send(json.dumps({"message": "Device A connected. Waiting for Device B."}))

        except Exception as e:
            await self.send(json.dumps({"statusCode": 500, "message": f"Error in Device A connection: {str(e)}"}))
            await self.close()

    async def handle_device_b_connection(self):
        """处理设备 B 的连接逻辑"""
        try:
            is_valid = await self.is_valid_b_session(self.session_id, self.access_token)
            if not is_valid:
                await self.send(json.dumps({
                    "statusCode": 400,
                    "message": "Invalid session_id or access_token"
                }))
                await self.close()
                return

            # 取消设备 A 的超时计时器
            if self.timer_task:
                self.timer_task.cancel()

            # 通知设备 A：设备 B 已连接
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "broadcast_message",
                    "message": {"message": "Device B connected. Ready to approve or reject."}
                }
            )
        except Exception as e:
            await self.send(json.dumps({"statusCode": 500, "message": f"Error in Device B connection: {str(e)}"}))
            await self.close()

    async def receive(self, text_data):
        """接收 WebSocket 消息"""
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if self.role == self.role_scaner:
                if action == "approve":
                    login_id = data.get("login_id")
                    login_type = data.get("login_type")
                    access_token = data.get("access_token")
                    await self.update_session_status(self.session_id, self.status_approved)
                    await self.notify_group({
                        "statusCode": 201,
                        "message": "User approved login",
                        "detailData": {
                            "type": self.status_approved,
                            "login_id": login_id,
                            "login_type": login_type,
                            "access_token": access_token
                        }
                    })
                elif action == "reject":
                    await self.update_session_status(self.session_id, self.status_rejected)
                    await self.notify_group({
                        "statusCode": 400,
                        "message": "User rejected login",
                        "detailData": {"type": self.status_rejected}
                    })
                    await self.clean_and_close_group()
                else:
                    await self.send(json.dumps({"statusCode": 400, "message": "Unknown action"}))
            elif self.role == self.role_gen:
                if action == "complete":
                    await self.notify_group({
                        "statusCode": 200,
                        "message": "Device A completed login process"
                    })
                    await self.clean_and_close_group()
        except json.JSONDecodeError:
            await self.send(json.dumps({"statusCode": 400, "message": "Invalid JSON format"}))
        except Exception as e:
            await self.send(json.dumps({"statusCode": 500, "message": f"Error during message processing: {str(e)}"}))
            await self.clean_and_close_group()

    async def notify_group(self, message):
        """发送通知给组内所有成员"""
        try:
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "broadcast_message", "message": message}
            )
        except Exception as e:
            print(f"Error notifying group: {e}")

    async def broadcast_message(self, event):
        """组内广播消息"""
        try:
            message = event["message"]
            await self.send(json.dumps(message))
        except Exception as e:
            print(f"Error broadcasting message: {e}")

    async def disconnect(self, close_code):
        """处理断开连接"""
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            if self.timer_task:
                self.timer_task.cancel()
        except Exception as e:
            print(f"Error during disconnect: {e}")

    async def close_after_timeout(self, timeout_seconds):
        """超时关闭 WebSocket"""
        try:
            await asyncio.sleep(timeout_seconds)
            await self.update_session_status(self.session_id, self.status_timeout)
            await self.notify_group({
                "statusCode": 400,
                "message": "Login timeout",
                "detailData": {"type": self.status_timeout}
            })
            await self.clean_and_close_group()
        except asyncio.CancelledError:
            print("Timeout task cancelled.")
        except Exception as e:
            print(f"Error during timeout: {e}")

    async def clean_and_close_group(self):
        """清理群组并关闭 WebSocket"""
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception as e:
            print(f"Error cleaning up group: {e}")
        finally:
            await self.close()

    @database_sync_to_async
    def is_valid_session(self, session_id):
        """验证设备 A 的 session_id 是否有效"""
        try:
            session = TempQrSession.objects.get(session_key=session_id)
            return session.expires_at > now()
        except TempQrSession.DoesNotExist:
            return False

    @database_sync_to_async
    def is_valid_b_session(self, session_id, access_token):
        """验证设备 B 的 session_id 和 access_token"""
        try:
            session = TempQrSession.objects.get(session_key=session_id)
            return session.access_token == access_token and session.expires_at > now()
        except TempQrSession.DoesNotExist:
            return False

    @database_sync_to_async
    def update_session_status(self, session_id, status):
        """更新 session 状态"""
        try:
            session = TempQrSession.objects.get(session_key=session_id)
            session.status = status
            session.is_active=False
            session.save()
        except TempQrSession.DoesNotExist:
            print(f"Session {session_id} does not exist.")

    @database_sync_to_async
    def update_session_success_status(self, session_id, status,login_id,login_type):
        """更新 session 状态"""
        try:
            user=UserProfile.objects.get(login_id=login_id,login_type=login_type)
            session = TempQrSession.objects.get(session_key=session_id)
            session.status = status
            session.user_id=user.user_id
            session.is_active = False
            session.save()
        except TempQrSession.DoesNotExist:
            print(f"Session {session_id} does not exist.")
