import json
import re
import secrets
from datetime import datetime
from idlelib.textview import ViewWindow
from urllib import request

from django.conf import settings
from django.db.models import Q
from django.forms import model_to_dict

from rest_framework.exceptions import ValidationError

import apps.CustomManager.accountManger.comm as com
from django.utils.timezone import now
import datetime
from apps.CustomManager.accountManger.VerifyParm import VerifyParm
from apps.CustomManager.form import UserRegistrationForm
from apps.CustomManager.models import UserProfile, UserTokens, UserSessions, TempQrSession
from apps.CustomManager.accountManger.AccountEventView import AccountEvent
from apps.CustomManager.serializers import UserProfileSerializer, UserLoginSerializer, UserLogoutSerializer, \
    refreshTokenSerializer, accessTokenSerializer, accessScanQrTokenSerializer


class AccessAuth(VerifyParm):

    def registerStatus(self, request):

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  #
            id_token=self.generate_id_token(serializer.data)
            data={
                'id_token': id_token,
                'user_id': serializer.data['user_id'],
                'name': serializer.data['name']
            }
            return self._getSuccessRespones(self.success,self.REGISTER_SUCCESS_MESSAGE,
                                            data)
        return self._getErrorRespones(self.code_failed,self.REGISTER_FAILED_MESSAGE,
                                      serializer.errors)

    def loginStatus(self,request):
        # 必须字段检查
        action = 'login'
        logger = AccountEvent()
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            login_id=serializer.data['login_id']
            login_type = serializer.data['login_type']
            user_id = serializer.data['user_id']
            try:
                user_data,user=self.getNewId_token(login_id,login_type)
                # 现在 user_dict 是一个字典，你可以打印它或者返回它


                user_agent, ip_address = self.getUserAgent(request)
                user_sessions = UserSessions.objects.filter(
                    user_id=user_id,
                    user_agent=user_agent,
                    ip_address=ip_address,
                    is_active=True
                )
                token_status = self.checkAccessToken(user_id, user_agent, ip_address)
                if user_sessions.exists() and not token_status:
                    dataResult = user_id + " had login the devices(" + user_agent + ")"
                    logger.log_user_action(user_id, action, False, ip_address, user_agent, dataResult)
                    return self._getErrorRespones(self.code_f_id_exist, self.LOGIN_FAILED_MESSAGE, dataResult)
                access_token, expiration_time = self.generate_access_token(login_id, user.password,user_agent)

                refresh_token = self.generate_refresh_token(user_agent)
                sessionStatus, sessionData = AccountEvent.create_session(user_id, access_token, user_agent,
                                                                 ip_address)
                if not sessionStatus:
                    logger.log_user_action(user_id, self.action_login, False, ip_address, user_agent, sessionData)
                    return self._getErrorRespones(self.code_f_id_exist, self.LOGIN_FAILED_MESSAGE, sessionData)
                data = {
                    "user_id": user_id,
                    "access_token": access_token,

                    # 60分钟的tokendata = {str} 'Traceback (most recent call last):\n  File "D:\\fatuodownload\\AutoUpgradeApp\\venv\\Lib\\site-packages\\rest_framework\\fields.py", line 437, in get_attribute\n    return get_attribute(instance, self.source_attrs)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^... View
                    "refresh_token": refresh_token,  # 刷新时间，长期有效，除非被注销
                    "id_token":user_data,
                    "token_type": "Bear",  # token类型
                    "expires_at": expiration_time,  # 60分钟过期时间

                }

                result = {
                    'result_code': self.success,
                    'message': f"{login_id} Login success",
                    'data': data
                }
                devices_data = {
                    "user_agent": user_agent,
                    "ip_address": ip_address

                }
                logger.log_user_action(user_id, self.action_login, True, ip_address, user_agent, data)
                logger.create_activity(user_id, self.action_login, devices_data)
                return self._getSuccessRespones(self.success,self.LOGIN_SUCCESS_MESSAGE,result)
            except Exception as e:
                err_data={f"login_id": f"The {str(e)} doesn't exist."}
                return self._getErrorRespones(self.code_f_id_exist,self.LOGIN_FAILED_MESSAGE,err_data)
        else:
            return self._getErrorRespones(self.code_f_id_exist, self.LOGIN_FAILED_MESSAGE, serializer.errors)


    def logoutStatus(self, request):
        logger = AccountEvent()

        authorization = request.headers.get('Authorization', None)
        user_agent, ip_address = self.getUserAgent(request)

        # 初始化序列化器，并将 authorization 传递到 context 中
        serializer = UserLogoutSerializer(data=request.data, context={
            'authorization': authorization,
            'user_agent':user_agent,
            'ip_address':ip_address
        })

        if serializer.is_valid():
            print("logout")
            print(serializer.data)
            serializer.data['user_agent']=user_agent
            serializer.data['ip_address']=ip_address
            user_id=serializer.data['user_id']


            logger.log_user_action(user_id, self.action_logout, True, ip_address, user_agent, self.LOGOUT_SUCCESS_MESSAGE)
            logger.create_activity(user_id,self.action_logout,serializer.data)
            return self._getSuccessRespones(self.success,self.LOGOUT_SUCCESS_MESSAGE,serializer.data)
        print(serializer.errors)
        login_id = request.headers.get('login_id')
        login_type = request.headers.get('login_type')
        user_id=self.verify_logout_exists(login_id,login_type)
        if user_id:
            logger.log_user_action(user_id, self.action_logout, False, ip_address, user_agent, serializer.errors)
        return self._getErrorRespones(self.code_failed,self.LOGOUT_FAILED_MESSAGE,serializer.errors)

    def refreshTokenStatus(self, request):
        logger = AccountEvent()
        auth_header = request.headers.get('Authorization')
        action = "refresh"
        user_agent, ip_address = self.getUserAgent(request)

        serializer = refreshTokenSerializer(data=request.data, context={'authorization': auth_header})

        print("refresh start------------")
        if serializer.is_valid():
            # 解析数据
            user_id = serializer.validated_data.get('user_id')
            old_access_token = serializer.validated_data.get('access_token')  # 这里是 refresh_token 而不是 access_token
            login_id = serializer.validated_data.get('login_id')
            password = serializer.validated_data.get('password')

            # 确保我们得到了所需的值
            print(f"User ID: {user_id}, Old Access Token: {old_access_token}, Login ID: {login_id}")
            login_id = request.data['login_id']
            login_type = request.data['login_type']
            try:
                # 生成旧的 session_key
                old_session_key = AccountEvent.generate_seeison_key(user_id, old_access_token, user_agent, ip_address)

                # 生成新的 access_token 和过期时间
                new_access_token, expiration_time = self.generate_access_token(login_id, password, user_agent)
                print(f"New Access Token: {new_access_token}, Expiration Time: {expiration_time}")

                # 更新 UserTokens
                user_token_content = UserTokens.objects.get(user_id=user_id, access_token=old_access_token,
                                                            is_active=True)
                user_token_content.access_token = new_access_token
                user_token_content.expires_at = expiration_time
                user_token_content.save()

                # 生成新的 session_key
                new_session_key = AccountEvent.generate_seeison_key(user_id, new_access_token, user_agent, ip_address)
                print(f"Old session key: {old_session_key}")
                print(f"New session key: {new_session_key}")
                # 更新 session 数据
                update_data = {
                    "session_key": new_session_key,
                    "last_activity": now(),
                    "login_method": "token",
                }

                session_data = AccountEvent.update_session(user_id, old_session_key, update_data)
                user = UserProfile.objects.get(
                    Q(login_id=login_id) & Q(login_type=login_type) & Q(user_id=user_id)
                )
                # 将 UserProfile 实例转换为字典
                user_dict = model_to_dict(user)
                user_dict['birthday'] = user_dict['birthday'].isoformat() if isinstance(user_dict['birthday'], (
                    datetime.date, datetime.datetime)) else user_dict['birthday']

                user_data = self.generate_id_token(user_dict)
                # 获取新令牌数据
                token_data_new = UserTokens.objects.get(user_id=user_id, access_token=new_access_token, is_active=True)
                token_data = {
                    "user_id": user_id,
                    "access_token": token_data_new.access_token,
                    "refresh_token": token_data_new.refresh_token,
                    "id_token":user_data,
                    "token_type": token_data_new.token_type,
                    "expires_at": token_data_new.expires_at
                }

                logger.log_user_action(user_id, self.action_refresh, True, ip_address, user_agent, self.LOGOUT_SUCCESS_MESSAGE)
                logger.create_activity(user_id, self.action_login, serializer.data)
                # 返回成功响应
                return self._getSuccessRespones(self.success, self.REFRESH_SUCCESS_MESSAGE, token_data)

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                logger.log_user_action(user_id, self.action_refresh, False, ip_address, user_agent,  {str(e)})
                return self._getErrorRespones(self.code_failed, self.REFRESH_FAILED_MESSAGE, str(e))

        else:
            login_id = request.data['login_id']
            login_type = request.data['login_type']
            user_id = self.verify_logout_exists(login_id, login_type)
            if user_id:
            # 如果序列化器无效，返回错误信息
                 logger.log_user_action(user_id, action, False, ip_address, user_agent, serializer.errors)
            return self._getErrorRespones(self.code_failed, self.REFRESH_FAILED_MESSAGE, serializer.errors)

    def accessTokenStatus(self,request):
        logger = AccountEvent()
        login_id=request.data.get('login_id')
        login_type = request.data.get('login_type')
        auth_header = request.headers.get('Authorization')

        user_agent, ip_address = self.getUserAgent(request)

        serializer = accessTokenSerializer(data=request.data,
                                           context={'authorization': auth_header})

        print("Token start------------")
        if serializer.is_valid():
            print(serializer.data)
            user_id=serializer.data['user_id']
            access_token = serializer.data['access_token']
            session_key = AccountEvent.generate_seeison_key(user_id, access_token, user_agent, ip_address)
            id_token,user=self.getNewId_token(login_id,login_type)
            new_access_token, new_expiration_time = self.getNewAccessToken(
                login_id, login_type, access_token, user_agent)
            new_session_key = AccountEvent.generate_seeison_key(user_id, new_access_token, user_agent, ip_address)

            try:

                User_session=UserSessions.objects.get(
                    Q(user_id=user) & Q(session_key=session_key)
                    & Q(is_active=True)
                )
                User_session.session_key=new_session_key
                User_session.login_method=self.action_token
                User_session.last_activity=now()
                User_session.save()
                token_data = {
                    "user_id": user_id,
                    "access_token": new_access_token,

                    "id_token": id_token,
                    "token_type": 'Bearer ',
                    "expires_at": new_expiration_time
                }
                logger.create_activity(user_id, self.action_login, serializer.data)
                logger.log_user_action(user_id, self.action_token, True, ip_address, user_agent, self.TOKEN_SUCCESS_MESSAGE)
                return self._getSuccessRespones(self.success,self.TOKEN_SUCCESS_MESSAGE,token_data)
            except UserSessions.DoesNotExist:
                AccountEvent.create_session(user_id,new_access_token,user_agent,ip_address)
                token_data = {
                    "user_id": user_id,
                    "access_token": new_access_token,
                    "id_token": id_token,
                    "token_type": 'Bearer ',
                    "expires_at": new_expiration_time
                }
                logger.create_activity(user_id, self.action_login, serializer.data)

                logger.log_user_action(user_id, self.action_token, True, ip_address, user_agent, self.TOKEN_SUCCESS_MESSAGE)
                return self._getSuccessRespones(self.success,self.TOKEN_SUCCESS_MESSAGE,token_data)
        user_id = self.verify_logout_exists(login_id, login_type)
        if user_id:
            print("")
            # 如果序列化器无效，返回错误信息
            logger.log_user_action(user_id, self.action_token, False, ip_address, user_agent, str(serializer.errors))
        return self._getErrorRespones(self.code_failed, self.TOKEN_FAILED_MESSAGE, serializer.errors)

    def modifyStatus(self, request):
        user_id = request.data.get('user_id')

        auth_header = request.headers.get('Authorization')
        try:
            updated_data = self._update_accountInfo(user_id, request.data, auth_header)
            print(updated_data)
            return self._getSuccessRespones(self.success,self.MODIFY_SUCCESS_MESSAGE,updated_data)  # 假设你有一个返回成功响应的方法
        except ValidationError as e:
            return self._getErrorRespones(self.code_f_id_other,self.MODIFY_FAILED_MESSAGE,str(e))  # 假设你有一个返回错误响应的方法

    def foundOutStatus(self, request):
        login_id = request.data.get('login_id')
        login_type = request.data.get('login_type')
        try:
            updated_data = self._found_out_account(login_id,login_type, request.data)
            print(updated_data)
            return self._getSuccessRespones(self.success, self.MODIFY_SUCCESS_MESSAGE, updated_data)  # 假设你有一个返回成功响应的方法
        except ValidationError as e:
            return self._getErrorRespones(self.code_f_id_other, self.MODIFY_FAILED_MESSAGE, str(e))  # 假设你有一个返回错误响应的方法


        pass

    def checkAccessToken(self, user_id, user_agent, ip_address):
        acountEvent=AccountEvent()
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
                token_session_key = acountEvent.generate_session_key(user_id, user_token, user_agent, ip_address)

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

    def generQrStatus(self, request):
        user_agent, ip_address = self.getUserAgent(request)
        secret_key=settings.SECRET_KEY
        try:
            session_key, access_token, expiration_time = self.generate_temp_token_and_session(user_agent, ip_address,
                                                                                              secret_key)
            result = {
                "session_key": session_key,
                "access_token": access_token,
                "expiration_time": expiration_time
            }
            return self._getSuccessRespones(self.success,self.GEN_SUCCESS_MESSAGE,result)
        except Exception as e:
            return self._getErrorRespones(self.code_failed,self.GEN_FAILED_MESSAGE,str(e))

    def verityQrStatus(self,request):

        logger = AccountEvent()
        login_id = request.data.get('login_id')
        login_type = request.data.get('login_type')
        auth_header = request.headers.get('Authorization')

        # user_agent, ip_address = self.getUserAgent(request)

        serializer = accessScanQrTokenSerializer(data=request.data,
                                           context={'authorization': auth_header})
        print("Qr token start------------")
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            access_token = serializer.data['access_token']
            ip_address = serializer.data['ip_address']
            user_agent = serializer.data['user_agent']
            id_token, user = self.getNewId_token(login_id, login_type)
            new_access_token, new_expiration_time = self.generate_access_token(user.user_id,
                                                                               user.password, user_agent)
            refresh_token = self.generate_refresh_token(user_agent)
            sessionStatus, sessionData = AccountEvent.create_session(user_id, access_token, user_agent,
                                                                     ip_address)
            if not sessionStatus:
                logger.log_user_action(user_id, self.action_login, False, ip_address, user_agent, sessionData)
                return self._getErrorRespones(self.code_f_id_exist, self.LOGIN_FAILED_MESSAGE, sessionData)
            data = {
                "user_id": user_id,
                "access_token": access_token,

                # 60分钟的tokendata = {str} 'Traceback (most recent call last):\n  File "D:\\fatuodownload\\AutoUpgradeApp\\venv\\Lib\\site-packages\\rest_framework\\fields.py", line 437, in get_attribute\n    return get_attribute(instance, self.source_attrs)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^... View
                "refresh_token": refresh_token,  # 刷新时间，长期有效，除非被注销
                "id_token": id_token,
                "token_type": "Bear",  # token类型
                "expires_at": new_expiration_time,  # 60分钟过期时间

            }

            result = {
                'result_code': self.success,
                'message': f"{login_id} Login success",
                'data': data
            }
            devices_data = {
                "user_agent": user_agent,
                "ip_address": ip_address

            }
            logger.log_user_action(user_id, self.action_login, True, ip_address, user_agent, data)
            logger.create_activity(user_id, self.action_login, devices_data)
            return self._getSuccessRespones(self.success, self.LOGIN_SUCCESS_MESSAGE, result)


        return self._getErrorRespones(self.success, self.LOGIN_FAILED_MESSAGE, serializer.errors)

    def veritySessionKey(self, session_key):
        """
        验证 session_key 是否有效
        """

        try:
            # 假设 QrCode 是你用来存储二维码状态的模型
            result=self._verity_session_key(session_key)
            return self._getSuccessRespones(self.success,self.GEN_SUCCESS_MESSAGE,result)

        except Exception as e:
            # 如果没有找到对应的 session_key，则返回错误
            return self._getErrorRespones(self.code_failed,self.GEN_FAILED_MESSAGE,str(e))

        # 如果二维码已经过期，返回错误



