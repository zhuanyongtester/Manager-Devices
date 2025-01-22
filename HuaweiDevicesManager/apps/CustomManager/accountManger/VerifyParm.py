import hashlib
import json
import re
import secrets
import uuid

from cryptography.fernet import Fernet
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime
import jwt
from django.db.models import Q
from django.utils.timezone import now
from rest_framework import status, response
from rest_framework.exceptions import ValidationError

from rest_framework.views import APIView
import apps.CustomManager.accountManger.comm as com
from HuaweiDevicesManager import settings
from apps.CustomManager.form import UserRegistrationForm
from apps.CustomManager.models import UserProfile, UserTokens, TempQrSession
from apps.CustomManager.serializers import UserProfileSerializer
from apps.base.BaseParm import BaseParm


class VerifyParm(APIView):
    def __init__(self, error_des=None,encryption_key=None):
        self.code_failed = status.HTTP_400_BAD_REQUEST
        self.success = 2000
        self.code_f_fields_null = 2001
        self.code_f_id = 2002
        self.code_f_id_exist = 2003
        self.code_f_id_other = 2004
        self.refresh_token_expiry_days = 30  # 刷新令牌的有效期（天）
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
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
        self.TOKEN_SUCCESS_MESSAGE="Token Login Success"
        self.TOKEN_FAILED_MESSAGE="Token Login Failed"
        self.MODIFY_SUCCESS_MESSAGE='Modify Success'
        self.MODIFY_FAILED_MESSAGE = 'Modify Failed'
        self.GEN_SUCCESS_MESSAGE = 'generate success'
        self.GEN_FAILED_MESSAGE = 'generate failed'
        self.action_login='login'
        self.action_logout='logout'
        self.action_refresh='refresh'
        self.action_token='token'

    def _getErrorRespones(self, result_code, message, err_data):
        response_data = {
            "statusCode": self.code_failed,
            "resultCode": result_code,
            "message": message,
            "detailData": err_data or {}
        }
        return response_data

    def _getSuccessRespones(self, result_code, message, success_data):
        response_data = {
            "statusCode": self.SUCCESS_201,
            "resultCode": result_code,
            "message": message,
            "detailData": success_data or {}
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

    def generate_temp_token_and_session(self,user_agent,ip_address, secret_key):

        # 创建唯一的 session_key
        session_key = str(uuid.uuid4())
        # 设置令牌的过期时间
        expiration_time = timezone.now() + timedelta(seconds=60)

        # 创建临时访问令牌（不含用户 ID，仅包含 session_key）
        payload = {
            'user_agent':user_agent,
            'session_key': session_key,
            'exp': expiration_time
        }
        access_token = jwt.encode(payload, secret_key, algorithm='HS256')
        try:
            # 保存临时会话到数据库，包括设备信息
            temp_session = TempQrSession.objects.create(
                session_key=session_key,
                access_token=access_token,
                expires_at=expiration_time,
                user_agent=user_agent,
                ip_address=ip_address,
                is_active=True
            )

            return session_key, access_token, expiration_time
        except Exception as e:
            raise ValidationError(str(e))

    def generate_refresh_token(self,device_info=None):

        raw_token = secrets.token_urlsafe(64)

        # 将设备信息转为 JSON 格式
        device_info_json = json.dumps(device_info or {})

        # 拼接令牌和设备信息
        combined_data = f"{raw_token}:{device_info_json}"

        # 加密令牌
        encrypted_token = self.fernet.encrypt(combined_data.encode()).decode()


        return encrypted_token
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

    def getNewAccessToken(self,login_id,login_type,old_access_token,device=None):
        try:
            user=UserProfile.objects.get(
                    Q(login_id=login_id)& Q(login_type=login_type))

            user_token_content = UserTokens.objects.get(
                Q(user_id=user) & Q(access_token=old_access_token) & Q(is_active=True)
            )
            new_access_token, new_expiration_time = self.generate_access_token(user.user_id,
                                                                       user.password, device)
            user_token_content.access_token = new_access_token
            user_token_content.expires_at = new_expiration_time
            user_token_content.save()
        except Exception as e:
            new_access_token=None
            new_expiration_time=now()
        return new_access_token,new_expiration_time
    def getNewId_token(self,login_id,login_type):
        import datetime
        try:
            user = UserProfile.objects.get(
                Q(login_id=login_id) & Q(login_type=login_type)
            )
            # 将 UserProfile 实例转换为字典
            user_dict = model_to_dict(user)
            user_dict['birthday'] = user_dict['birthday'].isoformat() if isinstance(user_dict['birthday'], (
                datetime.date, datetime.datetime)) else user_dict['birthday']

            user_data = self.generate_id_token(user_dict)
        except UserProfile.DoesNotExist:
            user_data=None
            user=None
        return user_data,user

    def _update_accountInfo(self, user_id, update_data, authorization):
        baseParm = BaseParm()  # 假设 BaseParm 是验证工具类
        if not user_id :
            raise ValidationError("user_id cannot be null")
        try:

            # 查找用户信息
            user = UserProfile.objects.get(user_id=user_id)
            baseParm.verity_access_token(user.user_id, authorization)
            # 验证 access token 是否有效

        except UserProfile.DoesNotExist:
            # 如果用户不存在，抛出 ValidationError
            raise ValidationError(f"The  {user_id} doesn't exist.")
        except Exception as e:
            # 捕获其他异常并返回详细错误信息
            raise ValidationError(str(e))  # 这里使用 str() 以确保错误信息是一个字符串

        # 用 Serializer 更新用户信息，partial=True 允许部分更新
        serializer = UserProfileSerializer(user, data=update_data, partial=True)

        if serializer.is_valid():
            # 如果数据有效，保存并返回更新后的数据
            updated_user = serializer.save()
            getData=serializer.data
            id_token,user=self.getNewId_token(getData['login_id'],getData['login_type'])
            result={
                "user_id":user.user_id,
                "id_token":id_token,
                "name":user.name
            }
            return result
        else:
            # 如果数据无效，抛出 ValidationError 并返回错误
            raise ValidationError(serializer.errors)

    def _found_out_account(self,login_id,login_type,update_data):
        try:
            if not login_id or not login_type:
                raise ValidationError("login_id or login_type cannot be null")
            if login_type == 'email' and '@' not in login_id:
                raise ValidationError({"login_id": "If login type is email, a valid email must be provided."})

            if login_type == 'phone' and not login_id.isdigit():
                raise ValidationError({"login_id": "If login type is phone, login_id must be numeric."})
            # 查找用户信息
            user = UserProfile.objects.get(Q(login_id=login_id)&Q(login_type=login_type))
            # 检查 update_data 是否只包含密码字段
            password_fields = {'password'}
            if set(update_data.keys()).issubset(password_fields):
                # 只修改了密码
                # 在此执行密码修改操作
                user.set_password(update_data['password'])  # 使用 set_password 方法来更新密码
                user.save()
                return {
                    "message": "Password updated successfully",
                    "user_id": user.user_id,
                    "id_token": self.getNewId_token(user.login_id, user.login_type)[0],  # 获取新 token
                }

            serializer = UserProfileSerializer(user, data=update_data, partial=True)

            if serializer.is_valid():
            # 如果数据有效，保存并返回更新后的数据
                updated_user = serializer.save()
            getData = serializer.data
            print(getData)
            id_token, user = self.getNewId_token(getData['login_id'], getData['login_type'])
            result = {
                "user_id": user.user_id,
                "id_token": id_token,
                "name": user.name
            }
            return result

        except UserProfile.DoesNotExist:
            raise ValidationError(f"The  {login_type} doesn't exist.")

    def _verity_session_key(self,session_key):
        try:
            # 查找会话
            qr_session = TempQrSession.objects.get(session_key=session_key)

            # 检查会话是否有效
            if qr_session.is_active and timezone.now() < qr_session.expires_at:
                raise ValidationError({
                    "status": "valid",
                    "session_key": session_key,
                    "expires_at": qr_session.expires_at,
                })
            else:
                raise ValidationError({
                    "status": "expired or inactive",
                    "session_key": session_key,
                })
        except TempQrSession.DoesNotExist:
            raise ValidationError({
                "status": "invalid",
                "message": "Session key not found."
            })
    def _verityQrStatus(self,request,session_key):
        if not session_key:
          raise ValidationError({
                "error": "session_key is missing."
            })

            # 查找会话
        try:
            qr_session = TempQrSession.objects.get(session_key=session_key)
        except TempQrSession.DoesNotExist:
            raise ValidationError({
                "error": "Session key not found."
            })

            # 检查会话是否过期
        if timezone.now() > qr_session.expires_at:
            qr_session.is_active = False  # 会话过期，标记为无效
            qr_session.save()
            raise ValidationError({
                "status": "expired",
                "message": "The QR session has expired."
            })

            # 会话有效，根据请求更新状态
        action = request.data.get('action', '')
        if action == 'approve':
            qr_session.status = 'approved'
            qr_session.save()
            raise ValidationError({
                "status": "approved",
                "message": "QR session approved."
            })
        elif action == 'reject':
            qr_session.status = 'rejected'
            qr_session.save()
            raise ValidationError({
                "status": "rejected",
                "message": "QR session rejected."
            })
        else:
            raise ValidationError({
                "status": "waiting",
                "message": "QR session is still waiting for approval."
            })