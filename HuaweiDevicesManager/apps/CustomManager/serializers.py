from django.db import transaction
from django.db.models import Max
from rest_framework import serializers
from .models import UserProfile, UserAuthLogs, UserSocial, UserInterests, UserTokens, UserSessions, UserEvent, UserPreferences

# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = UserProfile
        fields = [
             'user_id','name', 'gender', 'age', 'birthday', 'location', 'profession', 'language',
            'login_id', 'login_type', 'password', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},  # 加密保存密码
            'user_id': {'read_only': True}  # 标明 user_id 为只读，由服务器生成
        }

        def create(self, validated_data):
            login_id = validated_data.get('login_id')
            validated_data['user_id'] = "1000001"  # 设置生成的 user_id
            print(f"Generated user_id: {validated_data['user_id']}")  # 打印调试信息
            # Hash the password before saving
            password = validated_data.pop('password')
            user = UserProfile.objects.create(**validated_data)  # 创建用户并保存数据
            user.set_password(password)  # 使用 set_password 对密码加密
            user.save()  # 保存用户

            return user

            # # 检查 login_id 是否已存在
            # if not UserProfile.objects.filter(login_id=login_id).exists():
            #     max_user_id = UserProfile.objects.all().aggregate(Max('user_id'))['user_id__max']
            #     # 如果 login_id 不存在，则生成 user_id
            #     if max_user_id is None:
            #         new_user_id = 1000000  # 如果数据库中没有记录，则从1000000开始
            #     else:
            #         new_user_id = max_user_id + 1  # 当前最大值+1








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
