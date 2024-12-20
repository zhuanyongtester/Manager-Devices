import re
import secrets
from datetime import datetime
from idlelib.textview import ViewWindow
from urllib import request
import apps.CustomManager.accountManger.comm as com
from rest_framework import status, response

from rest_framework.views import APIView
import jwt
from apps.CustomManager import views
from apps.CustomManager.models import UserProfile
from apps.CustomManager.serializers import UserProfileSerializer


class AccessAuth(APIView):
    def __init__(self,error_des=None):
        self.code_failed = status.HTTP_400_BAD_REQUEST
        self.success = 2000
        self.code_f_fields_null=2001
        self.code_f_id=2002
        self.code_f_id_exist=2003
        self.code_f_id_other = 2004
        self.error_des = error_des
    def verify_fields(self,request,fields):
        missing_fields = [field for field in fields if field not in request.data]
        if missing_fields:
            return self._error_response(self.code_f_fields_null,com.RG_MISS_FIELDS,missing_fields)
        for field in fields:
            value = request.data.get(field, None)  # 获取字段值
            if isinstance(value, str):
                value = value.strip()
            if not value:
                return self._error_response(self.code_f_fields_null,
                                            f"{field.replace('_', ' ').capitalize()} is required and cannot be empty",
                                            [field])
    def verify_account_value(self,request):
        login_type = request.data['login_type']
        if login_type not in ['email', 'phone']:
            return self._error_response(self.code_f_id, "Invalid login type",
                                        {"login_type": "Invalid login type. Must be 'email' or 'phone'."})

        login_id = request.data['login_id']
        if login_type == 'email':
            email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
            if not re.match(email_pattern, login_id):
                return self._error_response(self.code_f_id, "Invalid email format", {"login_id": "Invalid email format."})

        elif login_type == 'phone':
            phone_pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
            if not re.match(phone_pattern, login_id):
                return self._error_response(self.code_f_id, "Invalid phone number format",
                                            {"login_id": "Invalid phone number format."})
    def verify_id_exist(self,request):
        login_type = request.data['login_type']
        login_id = request.data['login_id']
        return UserProfile.objects.filter(login_id=login_id, login_type=login_type).exists()
    def verify_login_status(self,request):
        login_type = request.data['login_type']
        login_id = request.data['login_id']
        password = request.data['password']
        user=UserProfile.objects.filter(login_id=login_id, login_type=login_type, password=password)
        if user.exists():
            return True,user.first()
        else:
            return False,None




    def registerStatus(self, request):
        # 必须字段检查
        required_fields = ['login_id', 'password', 'name', 'gender', 'birthday', 'location', 'age', 'language',
                           'login_type']
        error_fields = self.verify_fields(request, required_fields)
        if error_fields:
            return error_fields
        # 继续执行其他逻辑
        # 登录类型检查

        error_id_value=self.verify_account_value(request)
        if error_id_value:
            return error_id_value
        # 检查 login_id 和 login_type 是否已存在
        error_id_exist=self.verify_id_exist(request)
        if error_id_exist:
            login_id = request.data['login_id']
            return self._error_response(self.code_f_id_exist, f"{login_id} register failed", {"login_id": f"{login_id} already exists"})
        # 验证其他字段
        name = request.data['name'].strip()
        if not name:
            return self._error_response( self.code_f_id_other, "Name is required and cannot be empty",
                                        {"name": "Name is required and cannot be empty"})

        gender = request.data['gender']
        if gender not in ['male', 'female', 'other']:
            return self._error_response( self.code_f_id_other, "Invalid gender",
                                        {"gender": "please choose gender (male, female, or other)"})

        birthday = request.data['birthday']
        if not self.validate_birthday(birthday):
            return self._error_response( self.code_f_id_other, "Invalid birthday format or date",
                                        {"birthday": "Invalid birthday format or date"})

        location = request.data['location'].strip()
        if not location:
            return self._error_response( self.code_f_id_other, "Location is required and cannot be empty",
                                        {"location": "Location is required and cannot be empty"})

        age = request.data['age']
        try:
            age = int(age)
            if age < 0:
                raise ValueError()
        except ValueError:
            return self._error_response( self.code_f_id_other, "Invalid age", {"age": "Age must be a positive integer"})

        language = request.data['language'].strip()
        if not language:
            return self._error_response( self.code_f_id_other, "Language is required and cannot be empty",
                                        {"language": "Language is required and cannot be empty"})

    def validate_birthday(self, birthday):
        try:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            return birth_date < datetime.now()  # 确保出生日期小于当前日期
        except ValueError:
            return False

    def _error_response(self, result_code, message, errors=None):
        response_data = {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "resultCode": result_code,
            "message": message,
            "errors": errors or {}
        }
        return response.Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def _success_response(self, result_code, message, data=None):
        response_data = {
            "statusCode": status.HTTP_201_CREATED,
            "resultCode": result_code,
            "message": message,
            "data":data
        }
        return response.Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    def loginStatus(self,request):

        # 必须字段检查
        login_id = request.data['login_id']

        required_fields = ['login_id', 'password','login_type']
        error_fields = self.verify_fields(request, required_fields)

        if error_fields:
            return error_fields
        # 继续执行其他逻辑
        # 登录类型检查

        error_id_value = self.verify_account_value(request)
        if error_id_value:
            return error_id_value
        if not self.verify_id_exist(request):

            return self._error_response(self.code_f_id_exist, f"{login_id} Login failed",
                                 {"login_id": f"{login_id} not exists"})

        login_status,user_profile=self.verify_login_status(request)
        if not login_status:
            return self._error_response(self.code_f_id_exist, f"{login_id} Login failed",
                                 {"login_id": f"{login_id} of password don't match"})


    def login_success(self,request):
        login_id = request.data['login_id']
        password = request.data['password']
        login_status, user_profile = self.verify_login_status(request)
        access_token, expiration_time = self.generate_access_token(login_id, password)
        refresh_token = self.generate_refresh_token()
        print(user_profile)
        # if user_profile:
        #     serializer = UserProfileSerializer(user_profile, many=True)
        #     user_data = serializer.data
        # else:
        #     return self._error_response(self.code_f_id_exist, f"{login_id} Login failed",
        #                                 {"login_id": f"{login_id} not exists"})

        data = {
            "user_id":  user_profile.user_id,
            "access_token": access_token,
            # 60分钟的tokendata = {str} 'Traceback (most recent call last):\n  File "D:\\fatuodownload\\AutoUpgradeApp\\venv\\Lib\\site-packages\\rest_framework\\fields.py", line 437, in get_attribute\n    return get_attribute(instance, self.source_attrs)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^... View
            "refresh_token": refresh_token,  # 刷新时间，长期有效，除非被注销
            "token_type": "Bear",  # token类型
            "expires_at": expiration_time  # 60分钟过期时间
        }
        return data
    def generate_access_token(self,user_id, secret_key):
        import datetime
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        payload = {
            'user_id': user_id,
            'exp': expiration_time
        }
        access_token = jwt.encode(payload, secret_key, algorithm='HS256')
        return access_token, expiration_time

    def generate_refresh_token(self):
        return secrets.token_urlsafe(64)  # 长随机字符串作为 refresh_token