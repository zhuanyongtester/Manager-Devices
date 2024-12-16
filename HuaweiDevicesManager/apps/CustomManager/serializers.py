from rest_framework import serializers
from .models import UserProfile, UserAuthLogs, UserSocial, UserInterests, UserTokens, UserSessions, UserEvent, UserPreferences

# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = UserProfile
        fields = [
            'user_id', 'name', 'gender', 'age', 'birthday', 'location', 'profession', 'language',
            'login_id', 'login_type', 'password', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},  # 加密保存密码
        }

        def create(self, validated_data):
            # Hash the password before saving
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
        fields = '__all__'

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
