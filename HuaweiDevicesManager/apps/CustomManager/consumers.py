from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
import json

from apps.CustomManager.models import ChatModel


class QrCodeConsumer(WebsocketConsumer):
    def connect(self):

        self.accept()
        print("connect")
    def disconnect(self, close_code):
        print("disconnect")
        pass

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            self.send(text_data=text_data + " - Sent By Server")
        elif bytes_data:
            self.send(bytes_data=bytes_data)