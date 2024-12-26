import hashlib
import re
import secrets

from django.utils import timezone
from datetime import timedelta, datetime
import jwt
from django.db.models import Q
from rest_framework import status, response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
import apps.CustomManager.accountManger.comm as com
from HuaweiDevicesManager import settings
from apps.CustomManager.form import UserRegistrationForm
from apps.CustomManager.models import UserProfile, UserTokens


class VerifyParm(APIView):
    def __init__(self, error_des=None):
        self.code_failed = status.HTTP_400_BAD_REQUEST
        self.success = 2000
        self.code_f_fields_null = 2001
        self.code_f_id = 2002
        self.code_f_id_exist = 2003
        self.code_f_id_other = 2004
        self.error_des = error_des
        self.SUCCESS_201 = status.HTTP_201_CREATED
        self.SUCCESS_200 = status.HTTP_200_OK
        self.REGISTER_SUCCESS_MESSAGE="Register success"
        self.REGISTER_FAILED_MESSAGE = "Register Failed"
        self.LOGIN_FAILED_MESSAGE="Login Failed"
        self.LOGIN_SUCCESS_MESSAGE = "Login Success"
        self.LOGOUT_SUCCESS_MESSAGE="Logout Success"
        self.LOGOUT_FAILED_MESSAGE="Logout Failed"
        self.REFRESH_SUCCESS_MESSAGE="Refresh Token Success"
        self.REFRESH_FAILED_MESSAGE="Refresh Token Failed"

    def _getErrorRespones(self, result_code, message, err_data):
        response_data = {
            "statusCode": self.code_failed,
            "resultCode": result_code,
            "message": message,
            "errors": err_data or {}
        }
        return response_data

    def _getSuccessRespones(self, result_code, message, success_data):
        response_data = {
            "statusCode": self.SUCCESS_201,
            "resultCode": result_code,
            "message": message,
            "data": success_data or {}
        }
        return response_data

    def _is_valid_field(self, data, field):
        value = data.get(field, None)
        if isinstance(value, str):
            value = value.strip()
        return bool(value)

    def _get_validation_function(self, login_type):
        validation_map = {
            'email': self._validate_email,
            'phone': self._validate_phone
        }
        return validation_map.get(login_type)

    def _validate_email(self, email):
        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        return bool(re.match(email_pattern, email))

    def _validate_phone(self, phone):
        phone_pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
        return bool(re.match(phone_pattern, phone))

    def verify_fields(self, request, fields):
        data={}
        missing_fields = [field for field in fields if field not in request.data]
        if missing_fields:
            data={
                'result_code':self.code_f_fields_null,
                'message':com.RG_MISS_FIELDS,
                'errors':missing_fields

            }


        for field in fields:
            if not self._is_valid_field(request.data, field):
                data = {
                    'result_code': self.code_f_fields_null,
                    'message': f"{field.replace('_', ' ').capitalize()} is required and cannot be empty",
                    'errors': [field]
                }

        return data

    def verify_account_value(self, login_id,login_type):
        data={}
        if login_type not in ['email', 'phone']:
            data = {
                'result_code': self.code_f_id,
                'message': "Invalid login type",
                'errors':   {"login_type": "Invalid login type. Must be 'email' or 'phone'."}
            }


        validation_function = self._get_validation_function(login_type)

        if not validation_function:
            data = {
                'result_code': self.code_f_id,
                'message': f"Invalid {login_type} format",
                'errors': {"login_id": f"Invalid {login_type} format."}
            }


            return data

    def verify_id_exist(self, login_id,login_type):
        data={}
        if UserProfile.objects.filter(
            Q(login_id=login_id) & Q(login_type=login_type)
        ).exists():
            data={
                'result_code': self.code_f_id_exist,
                'message': f"Register {login_id} failed",
                'errors': {"login_id": f" {login_id} is exist."}
            }

        return data


    def verify_login_status(self, login_id,password,login_type):

        user = UserProfile.objects.filter(
            Q(login_id=login_id) & Q(login_type=login_type) & Q(password=password)
        ).first()
        if user:
            data = {}
            return data, user
        else:
            data = {
                'result_code': self.code_f_id_exist,
                'message': f"Register {login_id} failed",
                'errors': {"login_id": f" {login_id} don't exist."}
            }
            return data,None

    def verify_logout_exists(self, login_id,  login_type):
        try:
            user = UserProfile.objects.get(
                Q(login_id=login_id) & Q(login_type=login_type)
            )
            return user.user_id
        except UserProfile.DoesNotExist:
            return None
    def decode_access_token(self,access_token,secret_key):
        try:
            decoded_token = jwt.decode(access_token, secret_key, algorithms=['HS256'])
            return decoded_token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def generate_access_token(self,user_id, secret_key,device_id=None):
        expiration_time =timezone.now() + timedelta(hours=1)
        payload = {
            'user_id': user_id,
            'device_id':device_id,
            'exp': expiration_time
        }
        access_token = jwt.encode(payload, secret_key, algorithm='HS256')
        return access_token, expiration_time

    def generate_refresh_token(self):
        return secrets.token_urlsafe(64)  # 长随机字符串作为 refresh_token
    def getUserAgent(self,request):
        # 获取设备信息
        user_agent = request.headers.get('User-Agent', 'unknown_device')

        # 获取客户端 IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', 'unknown_ip')
        return user_agent,ip_address

    def _error_response(self, result_code, message, errors=None):
        response_data = {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "resultCode": result_code,
            "message": message,
            "errors": errors or {}
        }
        return response.Response(response_data, status=status.HTTP_400_BAD_REQUEST)


    def _getRespones(self,result):

        if  result:
            return self._error_response(result['result_code'], result['message'], result['errors'])

    def _success_response(self, result_code, message, errors=None):
        response_data = {
            "statusCode": status.HTTP_201_CREATED,
            "resultCode": result_code,
            "message": message,
            "data": errors or {}
        }
        return response.Response(response_data, status=status.HTTP_200_OK)


    def generate_id_token(self,user_data):
        import datetime
        self.validate_user_data(user_data)
        password=settings.SECRET_KEY
        """
        使用密码哈希生成密钥，并生成 id_token（JWT）。
        """
        # 使用 SHA256 哈希函数将密码哈希化（你也可以使用其他哈希算法）
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        payload = {
            'sub': user_data['user_id'],  # 用户唯一标识符
            'name': user_data['name'],  # 用户名称
            'gender': user_data['gender'],  # 用户性别
            'age': user_data['age'],  # 用户年龄
            'birthdate': user_data['birthday'],  # 用户生日
            'language': user_data['language'],  # 用户语言
            'login_id': user_data['login_id'],  # 登录ID
            'login_type': user_data['login_type'],  # 登录类型
            'iat': datetime.datetime.utcnow(),  # 签发时间
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # 过期时间，1小时后
        }

        # 使用哈希后的密码作为密钥生成并返回 id_token
        id_token = jwt.encode(payload, hashed_password, algorithm='HS256')
        return id_token

    def validate_user_data(self,user_data):
        required_fields = ['user_id', 'name', 'gender', 'age', 'birthday', 'language', 'login_id', 'login_type']

        # 确保 user_data 是字典并且包含所有必需的字段
        if not isinstance(user_data, dict):
            raise ValueError("user_data should be a dictionary")

        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")

        return True