from datetime import datetime
from idlelib.textview import ViewWindow
from urllib import request

from django.views import View
from requests import Response
from rest_framework import status

from apps.CustomManager import views
from apps.CustomManager.models import UserProfile


class AccessAuth(View):

      def registerStatus(self,request):
          login_id = request.data['login_id']
          password = request.data['password']
          birthday = request.data['birthday']
          login_id_exists = UserProfile.objects.filter(login_id=login_id).exists()
          if login_id_exists:
              return Response({"login_id": "该邮箱或手机号已被注册"}, status=status.HTTP_400_BAD_REQUEST)
          if '@' not in login_id and not login_id.isdigit():
              return Response({"login_id": "请输入有效的邮箱或手机号"}, status=status.HTTP_400_BAD_REQUEST)
          if len(password) < 8 or not any(char.isdigit() for char in password) or not any(
                  char.isupper() for char in password):
              return Response({"password": "密码至少包含8个字符，包括1个大写字母和1个数字"},
                              status=status.HTTP_400_BAD_REQUEST)

          if not birthday or not self.validate_birthday(birthday):
              return Response({"birthday": "请输入有效的出生日期"}, status=status.HTTP_400_BAD_REQUEST)


      def validate_birthday(self, birthday):
          try:
              birth_date = datetime.strptime(birthday, '%Y-%m-%d')
              return birth_date < datetime.now()  # 确保出生日期小于当前日期
          except ValueError:
              return False

      def validate_csrf_token(self, csrf_token):
          csrf_middleware = self.middleware.csrf
          return csrf_middleware._reject(request, csrf_token)

      def middleware(self):
          from django.middleware import csrf
          return csrf
