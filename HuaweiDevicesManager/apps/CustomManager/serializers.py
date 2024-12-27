import hashlib
import re

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from .models import UserProfile, UserAuthLogs, UserSocial, UserInterests, UserTokens, UserSessions, UserEvent, \
    UserPreferences, UserActivity
from apps.CustomManager.untils.mangertools import AccountUserManager
# UserProfile Serializer
class UserProfileSerializer(serializers.Serializer):  # 使用 Serializer，而非 ModelSerializer
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    name = serializers.CharField(max_length=100)
    gender = serializers.ChoiceField(choices=['male', 'female'])
    age = serializers.IntegerField()
    birthday = serializers.DateField()
    location = serializers.CharField(max_length=255)
    profession = serializers.CharField(max_length=255)
    language = serializers.ChoiceField(choices=['en', 'zh', 'es', 'fr'])
    login_id = serializers.CharField(max_length=255)
    login_type = serializers.ChoiceField(choices=['email', 'phone'])
    user_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_name(self, value):
        print(f"Validating name: {value}")
        if not value:
            raise ValidationError("Name cannot be empty.")
        if len(value) > 100:
            raise ValidationError("Name cannot exceed 100 characters.")
        return value

    def validate_age(self, value):
        if value < 0:
            raise ValidationError("Age cannot be negative.")
        return value

    def validate_birthday(self, value):
        if value > timezone.now().date():
            raise ValidationError("Birthday cannot be in the future.")
        return value

    def validate_gender(self, value):
        valid_genders = ['male', 'female']
        if value not in valid_genders:
            raise ValidationError(f"Gender must be one of {', '.join(valid_genders)}.")
        return value

    def validate_location(self, value):
        if len(value) > 255:
            raise ValidationError("Location cannot exceed 255 characters.")
        return value

    def validate_language(self, value):
        valid_languages = ['en', 'zh', 'es', 'fr']
        if value not in valid_languages:
            raise ValidationError(f"Language must be one of {', '.join(valid_languages)}.")
        return value

    def validate_login_id(self, value):
        login_type = self.initial_data.get('login_type')  # 获取当前提交的 login_type
        if login_type == 'email':
            # 如果是邮箱，检查格式是否正确
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                raise ValidationError("Invalid email address.")
        elif login_type == 'phone':
            # 如果是手机号，检查是否为数字
            if not value.isdigit():
                raise ValidationError("Login ID must be a valid phone number (digits only).")
        else:
            raise ValidationError("Invalid login type.")

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return value

    def validate(self, data):
        # 全局验证：确保 login_type 与 login_id 配对
        login_type = data.get('login_type')
        login_id = data.get('login_id')

        if login_type == 'email' and '@' not in login_id:
            raise ValidationError({"login_id": "If login type is email, a valid email must be provided."})

        if login_type == 'phone' and not login_id.isdigit():
            raise ValidationError({"login_id": "If login type is phone, login_id must be numeric."})
        if UserProfile.objects.filter(
            Q(login_id=login_id) & Q(login_type=login_type)
        ).exists():
            raise ValidationError({f"login_id": "the "+login_type+" had exists."})
        return data

    def create(self, validated_data):
        if 'password' not in validated_data:
            raise ValidationError({"password": "Password is required."})

        password = validated_data.pop('password')  # 从 validated_data 中提取密码
        # 手动创建 UserProfile 并加密密码
        user = UserProfile(**validated_data)  # 创建 UserProfile 实例
        user.password = self.genrate_new_password(password)
        user.save()  # 手动保存到数据库
        return user
    def genrate_new_password(self,password):
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
        return hashed_password
class UserLoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    login_id = serializers.CharField(max_length=255)
    login_type = serializers.ChoiceField(choices=['email', 'phone'])
    def validate_login_id(self, value):
        login_type = self.initial_data.get('login_type')  # 获取当前提交的 login_type
        if login_type == 'email':
            # 如果是邮箱，检查格式是否正确
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                raise ValidationError("Invalid email address.")
        elif login_type == 'phone':
            # 如果是手机号，检查是否为数字
            if not value.isdigit():
                raise ValidationError("Login ID must be a valid phone number (digits only).")
        else:
            raise ValidationError("Invalid login type.")

        return value
    def validate(self, data):
        # 全局验证：确保 login_type 与 login_id 配对
        login_type = data.get('login_type')
        login_id = data.get('login_id')
        password=data.get('password')
        new_password=hashlib.md5(password.encode('utf-8')).hexdigest()

        if login_type == 'email' and '@' not in login_id:
            raise ValidationError({"login_id": "If login type is email, a valid email must be provided."})

        if login_type == 'phone' and not login_id.isdigit():
            raise ValidationError({"login_id": "If login type is phone, login_id must be numeric."})
        try:
            user = UserProfile.objects.get(
                Q(login_id=login_id) & Q(login_type=login_type)
            )
        except UserProfile.DoesNotExist:
            raise ValidationError({f"login_id": f"The {login_type} doesn't exist."})

        # 使用 check_password 来验证密码
        if  user.password!=new_password:
            raise ValidationError({f"password": f"The {login_type} password doesn't match."})
        data["user_id"]=user.user_id
        print(data)
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 将 `user_id` 动态添加到返回数据中
        if hasattr(self, 'validated_data') and 'user_id' in self.validated_data:
            representation['user_id'] = self.validated_data['user_id']
        return representation
class UserLogoutSerializer(serializers.Serializer):
    login_id = serializers.CharField(required=True, allow_blank=False)
    login_type = serializers.ChoiceField(choices=['email', 'phone'], required=True)
    user_id = serializers.IntegerField(read_only=True)
    def validate_login_id(self, value):
        """根据 login_type 验证 login_id 的值。"""
        login_type = self.initial_data.get('login_type')  # 从请求数据中获取 login_type
        if login_type == 'email' and ('@' not in value or '.' not in value):
            raise serializers.ValidationError("The login_id must be a valid email.")
        if login_type == 'phone' and not value.isdigit():
            raise serializers.ValidationError("The login_id must be a valid phone number.")
        return value

    def validate(self, attrs):
        """全局验证，确保 header 中有 Authorization。"""
        authorization = self.context.get('authorization')  # 从 context 中获取 Authorization
        user_agent = self.context.get('user_agent')
        ip_address = self.context.get('ip_address')
        login_type = attrs.get('login_type')
        login_id = attrs.get('login_id')
        if not authorization:
            raise serializers.ValidationError({"authorization": "Authorization header is missing."})
        if not authorization.startswith("Bearer "):  # 验证格式
            raise serializers.ValidationError({"authorization": "Invalid authorization header format. Must start with 'Bearer '."})
        try:
            user = UserProfile.objects.get(
                Q(login_id=login_id) & Q(login_type=login_type)
            )
            getAccessToken = authorization.split(' ')[1]

            user_token_content = UserTokens.objects.get(
                Q(user_id=user) & Q(access_token=getAccessToken) & Q(is_active=True)
            )
            if user_token_content.expires_at < now():
                err_data={
                    'user_id':user.user_id,
                    "err_message":{f"access_token already Expired."}
                }
                raise ValidationError(err_data)
            session_key = self.generate_seeison_key(user.user_id,
                                                    getAccessToken,
                                                    user_agent,
                                                    ip_address)
            user_sessions = UserSessions.objects.get(
                Q(session_key=session_key) &Q(is_active=True) )
            user_token_content.is_active = False
            user_sessions.is_active = False
            user_token_content.save()
            user_sessions.save()
            attrs['user_id']=user.user_id
        except UserProfile.DoesNotExist:
            raise ValidationError({f"login_id": f"The {login_type} doesn't exist."})
        except UserTokens.DoesNotExist:
            raise ValidationError({f"access_token is invalid."})
        except UserSessions.DoesNotExist:
            raise ValidationError({f"your account dont login the {user_agent} "})
        return attrs


    def generate_seeison_key(self, user_id, access_token, user_agent, ip_address):
        user_id_str = str(user_id)
        user_agent_str = user_agent or "unknown_device"
        ip_address_str = ip_address or "unknown_ip"
        access_token_str = access_token or "unknown_token"

        # Concatenate data for session key
        raw_data = f"{user_id_str}:{user_agent_str}:{ip_address_str}:{access_token_str}"
        # Generate SHA-256 hash
        session_key = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        return session_key


class refreshTokenSerializer(serializers.Serializer):
    login_id = serializers.CharField(required=True, allow_blank=False)  # 登录ID，必填字段
    login_type = serializers.ChoiceField(choices=['email', 'phone'], required=True)  # 登录类型，必须选择 'email' 或 'phone'
    user_id = serializers.IntegerField(read_only=True)  # 用户ID，只读字段，自动生成
    refresh_token = serializers.CharField(max_length=100, required=True)  # 刷新令牌，最大长度为100，必填字段
    access_token = serializers.CharField(read_only=True)  # 刷新令牌，最大长度为100，必填字段
    password = serializers.CharField(read_only=True)
    def validate(self, data):
        """
        自定义校验方法，可以用于验证多个字段的组合条件。
        例如：确保 login_id 和 login_type 匹配。
        """
        auth_header = self.context.get('authorization')
        login_id = data.get('login_id')
        login_type = data.get('login_type')
        refresh_token=data.get('refresh_token')
        # 示例：可以检查 login_id 和 login_type 的组合
        if login_type == 'email' and '@' not in login_id:
            raise serializers.ValidationError({"login_id": "If login type is 'email', a valid email must be provided."})

        if login_type == 'phone' and not login_id.isdigit():
            raise serializers.ValidationError({"login_id": "If login type is 'phone', login_id must be numeric."})

        if not auth_header or auth_header != "refresh_token":
            raise serializers.ValidationError({"Authorization": "refresh_token type missing."})

        try:
            user = UserProfile.objects.get(
                Q(login_id=login_id) & Q(login_type=login_type)
            )
            user_token_content = UserTokens.objects.get(
                Q(user_id=user) & Q(refresh_token=refresh_token) & Q(is_active=True)
            )
            access_token=user_token_content.access_token
            data['user_id']=user.user_id
            data['password'] = user.password
            data['access_token']=access_token
        except UserProfile.DoesNotExist:
            raise ValidationError({f"login_id": f"The {login_type} doesn't exist."})
        except UserTokens.DoesNotExist:
            raise ValidationError({f"refresh_token already Expired."})
        return data


class accessTokenSerializer(serializers.Serializer):
    login_id = serializers.CharField(required=True, allow_blank=False)
    login_type = serializers.ChoiceField(choices=['email', 'phone'], required=True)
    user_id = serializers.IntegerField(read_only=True)
    access_token = serializers.CharField(read_only=True)  # 刷新令牌，最大长度为100，必填字段

    def validate_login_id(self, value):
        """根据 login_type 验证 login_id 的值。"""
        login_type = self.initial_data.get('login_type')  # 从请求数据中获取 login_type
        if login_type == 'email' and ('@' not in value or '.' not in value):
            raise serializers.ValidationError("The login_id must be a valid email.")
        if login_type == 'phone' and not value.isdigit():
            raise serializers.ValidationError("The login_id must be a valid phone number.")
        return value
    def validate(self, attrs):
        """全局验证，确保 header 中有 Authorization。"""
        authorization = self.context.get('authorization')  # 从 context 中获取 Authorization
        login_type = attrs.get('login_type')
        login_id = attrs.get('login_id')
        if not authorization:
            raise serializers.ValidationError({"authorization": "Authorization header is missing."})
        if not authorization.startswith("Bearer "):  # 验证格式
            raise serializers.ValidationError({"authorization": "Invalid authorization header format. Must start with 'Bearer '."})
        try:
            user = UserProfile.objects.get(
                Q(login_id=login_id) & Q(login_type=login_type)
            )
            getAccessToken = authorization.split(' ')[1]
            user_token_content = UserTokens.objects.get(
                Q(user_id=user) & Q(access_token=getAccessToken) & Q(is_active=True)
            )
            if user_token_content.expires_at < now():
                err_data = {
                    'user_id': user.user_id,
                    "err_message": {f"access_token already Expired."}
                }
                raise ValidationError(err_data)

            user_token_content.last_used_at=now()
            user_token_content.save()
            attrs['access_token']=getAccessToken
            attrs['user_id']=user.user_id
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({f"login_id": f"The {login_type} doesn't exist."})
        except UserTokens.DoesNotExist:
            raise ValidationError({f"access_token is invalid"})

        return attrs



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


