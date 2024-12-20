from rest_framework import serializers
from .models import UserProfile, UserAuthLogs, UserSocial, UserInterests, UserTokens, UserSessions, UserEvent, UserPreferences
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
        fields = '__all__'

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

# UserTokens Serializer
class UserTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTokens
        fields = [
            'user_id', 'access_token', 'refresh_token', 'token_type',
            'created_at', 'expires_at', 'last_used_at', 'is_active'
        ]
        extra_kwargs = {
            'user_id': {'read_only': True},  # 不允许前端传递 user_id
            'access_token': {'write_only': True},  # 访问令牌一般也不应返回给前端
            'refresh_token': {'write_only': True},  # 同样，刷新令牌也是敏感信息
        }

    def create(self, validated_data):
        user = UserTokens.objects.create(**validated_data)
        user.save()
        return user


# UserSessions Serializer
class UserSessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSessions
        fields = '__all__'

# UserEvent Serializer
class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvent
        fields = '__all__'
