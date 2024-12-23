from django.utils.timezone import now
from rest_framework import serializers
from .models import UserProfile, UserAuthLogs, UserSocial, UserInterests, UserTokens, UserSessions, UserEvent, \
    UserPreferences, UserActivity
from apps.CustomManager.untils.mangertools import AccountUserManager
# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = UserProfile
        fields = [
            'user_id',
            'name', 'gender', 'age', 'birthday', 'location', 'profession', 'language',
            'login_id', 'login_type', 'password', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},  # 加密保存密码
            'user_id': {'read_only': True},  # 不允许前端传递

        }


        def create(self, validated_data):
            password = validated_data.pop('password')
            user = UserProfile.objects.create(**validated_data)
            user.set_password(password)  # 使用 set_password 对密码加密
            user.save()
            return user

# UserAuthLogs Serializer
class UserAuthLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuthLogs
        fields = ["user_id",
                  "action", "timestamp", "ip_address", "device"
            , "success", "failure_reason"]
        # fields = '__all__'  # 或者列出字段

        def create(self, validated_data):
            user = UserAuthLogs.objects.create(**validated_data)
            user.save()
            return user

# UserSocial Serializer
class UserSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocial
        fields = '__all__'

# UserInterests Serializer
class UserInterestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInterests
        fields = '__all__'

# UserPreferences Serializer
class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = '__all__'

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model=UserActivity
        fields=[
            'user_id',
            "activity_type","activity_data"
        ]

        def create(self, validated_data):
            user = UserActivity.objects.create(**validated_data)
            user.save()
            return user
# UserTokens Serializer
class UserTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTokens
        fields = [
            'user_id', 'access_token', 'refresh_token', 'token_type',
            'created_at', 'expires_at', 'last_used_at', 'is_active'
        ]
        extra_kwargs = {
            # 'user_id': {'read_only': True},  # 不允许前端传递 user_id
            # 'access_token': {'write_only': True},  # 访问令牌一般也不应返回给前端
            # 'refresh_token': {'write_only': True},  # 同样，刷新令牌也是敏感信息
        }

    def create(self, validated_data):
        user = UserTokens.objects.create(**validated_data)
        user.save()
        return user


# UserSessions Serializer
class UserSessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSessions
        fields = ["user_id",
                  "session_key","user_agent","ip_address","last_activity"
                  ,"is_active","created_at","login_method"]

        def create(self, validated_data):
            user = UserSessions.objects.create(**validated_data)
            user.save()
            return user

        def update(self, instance, validated_data):
            """
            Update an existing session record.
            """
            # 更新字段的值
            instance.session_key = validated_data.get("session_key", instance.session_key)
            instance.user_agent = validated_data.get("user_agent", instance.user_agent)
            instance.ip_address = validated_data.get("ip_address", instance.ip_address)
            instance.last_activity = validated_data.get("last_activity", now())  # 默认当前时间
            instance.is_active = validated_data.get("is_active", instance.is_active)

            # 保存更新后的实例
            instance.save()
            return instance

# UserEvent Serializer
class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvent
        fields = '__all__'


