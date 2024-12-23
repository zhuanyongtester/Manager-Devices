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

    def _getSuccessRespones(self, result):

        if result:
            return self._success_response(result['result_code'], result['message'], result['data'])


