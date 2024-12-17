from django.shortcuts import render
from requests import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.CustomManager.accountManger.AccessAuthView import AccessAuth
from apps.CustomManager.models import UserProfile
from apps.CustomManager.serializers import UserProfileSerializer


# Create your views here.
class UserRegisterView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        if not csrf_token or not self.validate_csrf_token(csrf_token):
            return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            # 检查登录 ID 是否已存在
            self.registerStatus(request)
            user = serializer.save()  # 保存用户数据
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # 返回成功响应
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 返回错误信息