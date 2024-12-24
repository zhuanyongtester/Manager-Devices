import json

from django.shortcuts import render

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.CustomManager.accountManger.AccessAuthView import AccessAuth
from apps.CustomManager.models import UserProfile
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

        # 检查 registerStatus 的返回值
        if result.status_code == 200:  # 如果返回了错误响应
            serializer = UserTokensSerializer(data=result.data['data'])
            if serializer.is_valid():
                serializer.save()  # 保存用户数据
                successData = {
                    "statusCode": status.HTTP_201_CREATED,
                    "resultCode": 2000,
                    "message": "User Login successfully",
                    "data": serializer.data
                }

                return Response(successData, status=status.HTTP_201_CREATED)
        else:
            # 如果验证通过，进行数据保存
            return result

        # 如果序列化失败，返回错误
        return Response({
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "resultCode": 1001,
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        result = self.logoutStatus(request)

        # 检查 registerStatus 的返回值

        return result


class RefreshTokenView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)

        # 如果序列化失败，返回错误
        return self.refreshTokenStatus(request)

class AccessTokenView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)


        # 检查 registerStatus 的返回值

        return self.accessTokenStatus(request)





