import re
import secrets
from datetime import datetime
from idlelib.textview import ViewWindow
from urllib import request

from django.conf import settings
from django.utils.timezone import localtime
import jwt
from django.utils import timezone
from datetime import timedelta
import apps.CustomManager.accountManger.comm as com
from rest_framework import status, response
from django.utils.timezone import now
from rest_framework.views import APIView

from apps.CustomManager import views
from apps.CustomManager.accountManger.VerifyParm import VerifyParm
from apps.CustomManager.form import UserRegistrationForm
from apps.CustomManager.models import UserProfile, UserTokens, UserSessions
from apps.CustomManager.accountManger.AccountEventView import AccountEvent

class AccessAuth(VerifyParm):
    def __init__(self,error_des=None):
        self.code_failed = status.HTTP_400_BAD_REQUEST
        self.success = 2000
        self.code_f_fields_null=2001
        self.code_f_id=2002
        self.code_f_id_exist=2003
        self.code_f_id_other = 2004
        self.error_des = error_des



    def registerStatus(self, request):
        # 必须字段检查

        form = UserRegistrationForm(request.data)
        if not form.is_valid():
            result = {
                'result_code': self.code_f_id_other,
                'message': f"Invalid input",
                'errors': form.errors
            }
            return self._getRespones(result)
        login_id = request.data.get('login_id')
        login_type = request.data.get('login_type')
        result = self.verify_account_value(login_id, login_type)
        if result:
            return self._getRespones(result)
        result = self.verify_id_exist(login_id, login_type)
        if result:
            return self._getRespones(result)


    def loginStatus(self,request):
        # 必须字段检查

        required_fields = ['login_id', 'password','login_type']
        error_fields = self.verify_fields(request, required_fields)
        action = 'login'
        if error_fields:

            return self._getRespones(error_fields)
        # 继续执行其他逻辑
        # 登录类型检查
        login_id = request.data['login_id']
        login_type = request.data['login_type']

        error_id_value = self.verify_account_value(login_id,login_type)
        if error_id_value:
            return self._getRespones(error_id_value)

        if not self.verify_id_exist(login_id,login_type):
            result = {
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': {"login_id": f"{login_id} not exists"}
            }
            return self._getRespones(result)
        password = request.data['password']
        data,user_profile=self.verify_login_status(login_id,password,login_type)
        if  data:

            return  self._getRespones(data)

        user_agent, ip_address = self.getUserAgent(request)
        # session_key=AccountEvent.generate_seeison_key(user_profile.user_id,access_token,user_agent,ip_address)
        user_sessions = UserSessions.objects.filter(
            user_id=user_profile.user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            is_active=True
        )
        token_status=self.checkAccessToken(user_profile.user_id,user_agent,ip_address)
        if user_sessions.exists() and not token_status:
            dataResult = user_profile.user_id + " had login the devices(" + user_agent + ")"
            result={
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': dataResult
            }
            return self._getRespones(result)
        access_token, expiration_time = self.generate_access_token(login_id, password)
        refresh_token = self.generate_refresh_token()
        sessionStatus, sessionData = AccountEvent.create_session(user_profile.user_id, access_token, user_agent,
                                                                 ip_address)
        if not sessionStatus:
            result = {
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': sessionData
            }
            AccountEvent.log_user_action(user_profile.user_id, action, ip_address, user_agent, sessionData)
            return self._getRespones(result)
        data = {
            "user_id": user_profile.user_id,
            "access_token": access_token,
            # 60分钟的tokendata = {str} 'Traceback (most recent call last):\n  File "D:\\fatuodownload\\AutoUpgradeApp\\venv\\Lib\\site-packages\\rest_framework\\fields.py", line 437, in get_attribute\n    return get_attribute(instance, self.source_attrs)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^... View
            "refresh_token": refresh_token,  # 刷新时间，长期有效，除非被注销
            "token_type": "Bear",  # token类型
            "expires_at": expiration_time,  # 60分钟过期时间

        }
        result = {
            'result_code': self.success,
            'message': f"{login_id} Login success",
            'data': data
        }

        AccountEvent.log_user_action(user_profile.user_id,action,ip_address,user_agent,None)
        return self._getSuccessRespones(result)


    def logoutStatus(self, request):

        required_fields = ['login_id', 'login_type']
        error_fields = self.verify_fields(request, required_fields)
        if error_fields:
            return self._getRespones(error_fields)
        login_id = request.data['login_id']
        login_type = request.data['login_type']
        error_id_value = self.verify_account_value(login_id, login_type)
        if error_id_value:
            return self._getRespones(error_id_value)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            err_data={"access_token": "missing access token."}
            result={
                'result_code': self.code_f_id,
                'message': f"Invalid access token",
                'errors': err_data
            }
            return self._getRespones(result)
        if not self.verify_id_exist(login_id,login_type):
            err_data = login_id + ":don't  exist"
            result = {
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': err_data
            }
            return self._getRespones(result)
        user_profile = UserProfile.objects.filter(login_id=login_id, login_type=login_type)
        if not user_profile.exists():
            err_data = login_id + ":don't  exist"
            result = {
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': err_data
            }
            return self._getRespones(result)
        token = auth_header.split(' ')[1]
        user_agent, ip_address = self.getUserAgent(request)
        try:
            # 获取当前用户的令牌信息
            user_profile = UserProfile.objects.filter(login_id=login_id, login_type=login_type).first()
            user_token_content = UserTokens.objects.filter(user_id=user_profile, access_token=token, is_active=True)
            session_key = AccountEvent.generate_seeison_key(user_profile.user_id,
                                                            token, user_agent, ip_address)
            user_sessions = UserSessions.objects.filter(session_key=session_key,is_active=True)
            # 标记所有令牌为无效
            if user_token_content.exists() and user_sessions.exists():
                user_token_content.update(is_active=False)
                user_sessions.update(is_active=False)
                data={
                    "user_agent":user_agent,
                    "ip_address":ip_address

                }
                result = {
                    'result_code': self.success,
                    'message': f"{login_id} logout success",
                    'data': data
                }
                return self._getSuccessRespones(result)
            else:
                data = "access_token had Expired"
                result = {
                    'result_code': self.code_f_id_other,
                    'message': f"{login_id} logout failed",
                    'errors': data
                }
                return self._getRespones(result)
        except Exception as e:

            data = str(e)
            result = {
                'result_code': self.code_f_id_other,
                'message': f"{login_id} logout failed",
                'errors': data
            }
            return self._getRespones(result)

    def refreshTokenStatus(self, request):
        required_fields = ['login_id', 'refresh_token', 'login_type']
        error_fields = self.verify_fields(request, required_fields)
        if error_fields:
            return self._getRespones(error_fields)

        login_id = request.data['login_id']
        login_type = request.data['login_type']
        refresh_token = request.data['refresh_token']

        # 验证账号值
        error_id_value = self.verify_account_value(login_id, login_type)
        if error_id_value:
            return self._getRespones(error_id_value)

        # 验证 Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != "refresh_token":
            return self._getRespones({
                'result_code': self.code_f_id,
                'message': "Invalid access token",
                'errors': {"Authorization": "refresh_token type missing."}
            })

        # 验证用户是否存在
        if not self.verify_id_exist(login_id, login_type):
            return self._getRespones({
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': f"{login_id}: don't exist"
            })

        user_profile = UserProfile.objects.filter(login_id=login_id, login_type=login_type)
        if not user_profile.exists():
            return self._getRespones({
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': f"{login_id}: don't exist"
            })

        try:
            # 验证令牌
            user_token_content = UserTokens.objects.filter(
                user_id=user_profile.first(), refresh_token=refresh_token, is_active=True
            )
            if not user_token_content.exists():
                return self._getRespones({
                    'result_code': self.code_f_id_exist,
                    'message': f"{login_id} Login failed",
                    'errors': "refresh_token has expired"
                })

            # 获取用户代理和 IP 地址
            user_agent, ip_address = self.getUserAgent(request)

            # 生成旧的会话密钥
            old_session_key = AccountEvent.generate_seeison_key(
                user_profile.first().user_id, user_token_content.first().access_token, user_agent, ip_address
            )

            # 更新令牌
            access_token, expiration_time = self.generate_access_token(
                user_profile.first().login_id, user_profile.first().password
            )
            user_token_content.update(access_token=access_token, expires_at=expiration_time)

            # 生成新的会话密钥
            new_session_key = AccountEvent.generate_seeison_key(
                user_profile.first().user_id, access_token, user_agent, ip_address
            )

            # 更新会话
            update_data = {
                "session_key": new_session_key,
                "last_activity": now(),
                "login_method": "token",
            }
            session_data = AccountEvent.update_session(
                user_profile.first(), old_session_key, update_data
            )

            # 获取新令牌数据
            token_data_new = UserTokens.objects.filter(
                user_id=user_profile.first(), access_token=access_token, is_active=True
            ).first()
            token_data = {
                "user_id": user_profile.first().user_id,
                "access_token": token_data_new.access_token,
                "refresh_token": token_data_new.refresh_token,
                "token_type": token_data_new.token_type,
                "expires_at": token_data_new.expires_at
            }

            return self._getSuccessRespones({
                'result_code': self.success,
                'message': "Token refresh success",
                'data': {
                    "token_data": token_data,
                    "session_data": session_data
                }
            })

        except Exception as e:
            return self._getRespones({
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': str(e)
            })

    def accessTokenStatus(self,request):
        login_id = request.data['login_id']
        login_type = request.data['login_type']
        login_method = "token"
        required_fields = ['login_id', 'login_type']
        error_fields = self.verify_fields(request, required_fields)
        if error_fields:
            return self._getRespones(error_fields)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            err_data = {"access_token": "missing access token."}
            result = {
                'result_code': self.code_f_id,
                'message': f"Invalid access token",
                'errors': err_data
            }
            return self._getRespones(result)
        if not self.verify_id_exist(login_id, login_type):
            err_data = login_id + ":don't  exist"
            result = {
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': err_data
            }
            return self._getRespones(result)
        user_profile = UserProfile.objects.filter(login_id=login_id, login_type=login_type)
        if not user_profile.exists():
            err_data = login_id + ":don't  exist"
            result = {
                'result_code': self.code_f_id_exist,
                'message': f"{login_id} Login failed",
                'errors': err_data
            }
            return self._getRespones(result)



        try:
            token = auth_header.split(' ')[1]  # 提取Bearer后面的token
            # 获取当前用户的令牌信息
            user_profile = UserProfile.objects.filter(login_id=login_id, login_type=login_type)

            user_tokens = UserTokens.objects.filter(user_id=user_profile.first(), access_token=token,
                                                    is_active=True)
            if not user_tokens.exists():
                err_data = "access_token had Expired"
                result = {
                    'result_code': self.code_f_id_other,
                    'message': f"{login_id} Login failed",
                    'errors': err_data
                }
                return self._getRespones(result)

            user_agent, ip_address = self.getUserAgent(request)
            token_expires = user_tokens.first().expires_at
            local_time = localtime(token_expires)
            if local_time <= now():
                err_data = "access_token had Expired"
                result = {
                    'result_code': self.code_f_id_other,
                    'message': f"{login_id} Login failed",
                    'errors': err_data
                }
                return self._getRespones(result)

            else:
                user_tokens.update(last_used_at=now())
                user_sessions = UserSessions.objects.filter(user_id=user_profile.first(),
                                                            user_agent=user_agent,
                                                            ip_address=ip_address,
                                                            is_active=True)
                if user_sessions.exists():
                    new_session_key = AccountEvent.generate_seeison_key(user_profile.first().user_id, token, user_agent,
                                                                        ip_address)
                    update_data = {
                        "session_key": new_session_key,
                        "last_activity": now(),
                        "login_method": login_method,
                    }
                    session_data = AccountEvent.update_session(user_profile.first(), user_sessions.first().session_key,
                                                               update_data)
                    data={

                        "session_data":session_data
                    }
                    result = {
                        'result_code': self.code_f_id_other,
                        'message': f"token Login update success",
                        'data': data
                    }
                    return self._getSuccessRespones(result)
                status, session_data = AccountEvent.create_session(user_profile.first().user_id, token, user_agent, ip_address,
                                                           login_method)
                data = {

                    "session_data": session_data
                }
                result = {
                    'result_code': self.code_f_id_other,
                    'message': f"token Login create success",
                    'data': data
                }
                return self._getSuccessRespones(result)

            # 标记所有令牌为无效
        except Exception as e:

            data = str(e)
            result = {
                'result_code': self.code_f_id_other,
                'message': f"token Login failed",
                'errors': data
            }
            return self._getRespones(result)

    def checkAccessToken(self, user_id, user_agent, ip_address):
        try:
            # 查找匹配的用户会话
            user_session = UserSessions.objects.filter(
                Q(user_id=user_id) &
                Q(user_agent=user_agent) &
                Q(ip_address=ip_address)
            ).first()

            # 如果未找到会话，返回 True，表示需要重新登录
            if not user_session:
                return False

            # 查找用户的所有令牌
            user_tokens = UserTokens.objects.filter(user_id=user_id)

            # 遍历用户的令牌
            for user_token in user_tokens:
                # 生成会话密钥进行比较
                token_session_key = AccountEvent.generate_session_key(user_id, user_token, user_agent, ip_address)

                # 检查会话密钥是否匹配
                if user_session.session_key == token_session_key:
                    # 检查令牌是否已过期
                    if user_token.expires_at <= now():
                        user_session.update(is_active=False)
                        return True  # 令牌已过期，需要重新登录
                    else:
                        return False  # 令牌有效，不需要重新登录

            # 如果没有找到匹配的令牌，返回 True
            return False

        except Exception as e:
            # 记录异常（如果需要）
            return False  # 出现异常，默认需要重新登录


