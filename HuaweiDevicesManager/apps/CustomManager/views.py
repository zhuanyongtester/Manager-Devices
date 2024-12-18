from django.shortcuts import render

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.CustomManager.accountManger.AccessAuthView import AccessAuth
from apps.CustomManager.models import UserProfile
from apps.CustomManager.serializers import UserProfileSerializer


# Create your views here.
class UserRegisterView(AccessAuth):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserProfileSerializer(data=request.data)
        result = self.registerStatus(request)
        if serializer.is_valid():
            serializer.save()  # 保存用户数据
            successData={
                "statusCode": status.HTTP_201_CREATED,
                "resultCode": 2000,
                "message": "User registered successfully",
                "data": serializer.data
            }
            # 检查登录 ID 是否已存在

            return Response(successData, status=status.HTTP_201_CREATED)  # 返回成功响应

        return result