import json
import time

from django.http import HttpResponse
from django.shortcuts import render
import asyncio

from dwebsocket import accept_websocket
from dwebsocket.decorators import accept_websocket
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.CustomManager.accountManger.AccessAuthView import AccessAuth
from apps.CustomManager.models import UserProfile
from apps.CustomManager.serializers import UserProfileSerializer, UserTokensSerializer
from dwebsocket import require_websocket

class UserRegisterView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        result = self.registerStatus(request)
        return Response(result)
        # 检查 registerStatus 的返回值
        # if result and result.status_code == 400:  # 如果返回了错误响应
        #     return result
        #
        # # 如果验证通过，进行数据保存
        # serializer = UserProfileSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()  # 保存用户数据
        #     successData = {
        #         "statusCode": status.HTTP_201_CREATED,
        #         "resultCode": 2000,
        #         "message": "User registered successfully",
        #         "data": serializer.data
        #     }
        #     return Response(successData, status=status.HTTP_201_CREATED)
        #
        # # 如果序列化失败，返回错误
        # return Response({
        #     "statusCode": status.HTTP_400_BAD_REQUEST,
        #     "resultCode": 1001,
        #     "message": "Invalid data",
        #     "errors": serializer.errors
        # }, status=status.HTTP_400_BAD_REQUEST)
class UserLoginView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        result = self.loginStatus(request)
        print(result['statusCode'])
        if result and result['statusCode']==201:
            data=result['detailData']
            print(data)

            serializer = UserTokensSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response(result)

class UserLogoutView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        result = self.logoutStatus(request)

        # 检查 registerStatus 的返回值

        return Response(result)


class RefreshTokenView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        result=self.refreshTokenStatus(request)
        # 如果序列化失败，返回错误
        return Response(result)

class AccessTokenView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)


        # 检查 registerStatus 的返回值
        result=self.accessTokenStatus(request)
        return Response(result)


class AccountModifyView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)

        # 检查 registerStatus 的返回值
        result = self.modifyStatus(request)
        return Response(result)

class FoundOutAccountView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)

        # 检查 registerStatus 的返回值
        result = self.foundOutStatus(request)
        return Response(result)

class GenerateQrUrlView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def get(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)

        # 检查 registerStatus 的返回值
        result = self.generQrStatus(request)
        return Response(result)
class VerifyQrUrlView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图


    def get(self,request,session_key, *args, **kwargs):
        result=self.veritySessionKey(session_key)
        return Response(result)

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)

        # 检查 registerStatus 的返回值
        result = self.verityQrStatus(request)
        return Response(result)

class WebSocketView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    @require_websocket
    def websocket_connect(self, request, session_id, *args, **kwargs):

        # WebSocket连接时的处理
        print(f"WebSocket connected with session_id: {session_id}")
        self.ws = request.websocket
        self.session_id = session_id
        self.ws.send(json.dumps({
            'message': f'Connected to session {session_id}',
            'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        }))

    @require_websocket
    def websocket_receive(self, request, session_id, *args, **kwargs):
        # 接收到客户端消息时的处理
        message = request.websocket.read()
        print(f"Received message from session {session_id}: {message}")
        if not request.is_websocket():  # 判断是不是websocket连接
            try:  # 如果是普通的http方法
                message = request.GET['message']
                return HttpResponse(message)
            except:
                return HttpResponse("this is a websocket url!")
        response_data = {
            'message': 'Message received',
            'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            'received_message': message.decode()
        }
        self.ws.send(json.dumps(response_data))

    @require_websocket
    def websocket_disconnect(self, request, session_id, *args, **kwargs):
        # WebSocket断开连接时的处理
        print(f"WebSocket disconnected with session_id: {session_id}")
@accept_websocket
def echo(request):
    if not request.is_websocket():  # 判断是不是websocket连接
        try:  # 如果是普通的http方法
            message = request.GET['message']
            return HttpResponse(message)
        except:
            return HttpResponse("this is a websocket url!")
    else:
        print("userid")
        for message in request.websocket:
            str = message.decode('utf-8')
            print("Client msg: " + str)
            str = "server's msg: " + str
            request.websocket.send(str)  # 发送消息到客户端


@require_websocket
def echo_once(request):
    '''只能发送一次消息就断开连接'''
    message = request.websocket.wait()
    str = message.decode('utf-8')
    print("Client msg: " + str)
    str = "server's msg: " + str
    request.websocket.send(str)