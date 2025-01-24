import json
import time

from django.http import HttpResponse
from django.shortcuts import render
import asyncio

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.CustomManager.accountManger.AccessAuthView import AccessAuth
from apps.CustomManager.models import UserProfile, ChatModel
from apps.CustomManager.serializers import UserProfileSerializer, UserTokensSerializer


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

