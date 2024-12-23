import json

from django.utils.timezone import now
from rest_framework.views import APIView
import uuid
import hashlib
from datetime import datetime
from apps.CustomManager.models import UserSessions, UserAuthLogs
from apps.CustomManager.serializers import UserSessionsSerializer, UserAuthLogsSerializer, UserActivitySerializer


class AccountEvent(APIView):

    @classmethod
    def create_session(cls,user_id,access_token,user_agent=None,ip_address=None,login_method='password'):
        if user_agent is None:
            user_agent="unknown_device device"
        if ip_address is None:
            ip_address="unknown_device ip address"
        session_key=cls.generate_seeison_key(user_id,access_token,user_agent,ip_address)
        data={
            "user_id": user_id,
            "session_key": session_key,
            "user_agent": user_agent,
            "ip_address":ip_address,
            "last_activity": now(),
            "is_active": True,
            "created_at":now(),
            "login_method": login_method,
        }

        serializer = UserSessionsSerializer(data=data)
        if serializer.is_valid():
            session = serializer.save()
            status=True
            dataResult=serializer.data
        else:
            status=False
            dataResult=serializer.errors
        return status,dataResult

    def update_session(user_id,session_key, update_data):
        try:
           session = UserSessions.objects.get(user_id=user_id,session_key=session_key)
        except UserSessions.DoesNotExist:

            update_session_data="session_id don't exist"
            return update_session_data

        serializer = UserSessionsSerializer(session, data=update_data, partial=True)  # partial=True 允许部分更新
        if serializer.is_valid():
            updated_session = serializer.save()

            update_session_data=serializer.data

        else:

            update_session_data = serializer.errors
        return update_session_data

    @classmethod
    def generate_seeison_key(cls, user_id, access_token, user_agent, ip_address):
        user_id_str = str(user_id)
        user_agent_str = user_agent or "unknown_device"
        ip_address_str = ip_address or "unknown_ip"
        access_token_str = access_token or "unknown_token"

        # Concatenate data for session key
        raw_data = f"{user_id_str}:{user_agent_str}:{ip_address_str}:{access_token_str}"
        # Generate SHA-256 hash
        session_key = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        return session_key

    @classmethod
    def log_user_action(cls,user_id, action, success, ip_address, device, failure_reason=None):
        if device is None:
            device = "unknown_device device"
        if ip_address is None:
            ip_address = "unknown_device ip address"

        data={
                "user_id":user_id ,  # 如果失败，user_id 可能为空
                "action":action,
                "timestamp":now(),
                "ip_address":ip_address,
                "device":device,
                "success":success,
                "failure_reason":failure_reason
            }

        serializer = UserAuthLogsSerializer(data=data)

        if serializer.is_valid():
            # 保存新记录
            user=serializer.save()
            print("log_user_action:"+str(serializer.data))
        else:
            print("log_user_action:"+str(serializer.errors))

    @classmethod
    def create_activity(cls, user_id, activity_type,  activity_data):
        if activity_data:
              activity_data_str = json.dumps(activity_data)
        else:
            activity_data_str={}
        data = {
            "user_id": user_id,  # 如果失败，user_id 可能为空
            "activity_type": activity_type,
            "activity_data": activity_data_str,
            "activity_time": now(),

        }

        serializer =UserActivitySerializer(data=data)

        if serializer.is_valid():
            # 保存新记录
            user = serializer.save()
            print("create_activity:"+str(serializer.data))
        else:
            print("create_activity:"+str(serializer.errors))
