import re

from django.db import models
from django.utils.timezone import now


class UserIdCounter(models.Model):
    counter_name = models.CharField(max_length=50, unique=True)
    current_value = models.PositiveIntegerField(default=1000000)  #
# Create your models here.
class UserProfile(models.Model):
    user_id = models.CharField(max_length=255, unique=True, primary_key=True,verbose_name="用户唯一标识符")
    name = models.CharField(max_length=100, verbose_name="用户姓名")
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], verbose_name="性别")
    age = models.IntegerField(verbose_name="年龄")
    birthday = models.DateField(verbose_name="出生日期")
    location = models.CharField(max_length=255, verbose_name="用户所在位置")
    profession = models.CharField(max_length=100, verbose_name="职业")
    language = models.CharField(max_length=10, verbose_name="语言偏好")
    login_id = models.CharField(max_length=255, unique=True, verbose_name="用户邮箱或手机号")
    login_type = models.CharField(max_length=10, choices=[('email', 'Email'), ('phone', 'Phone')],
                                  verbose_name="用户注册方式")
    password = models.CharField(max_length=255, verbose_name="用户密码")
    created_at = models.DateTimeField(default=now, verbose_name="账户创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="账户信息更新时间")

    def __str__(self):
        return self.name

    @classmethod
    def get_user_id(cls, login_id, login_type, password):
        try:
            # 查询匹配用户
            user = cls.objects.get(login_id=login_id, login_type=login_type, password=password)
            return user
        except cls.DoesNotExist:
            return None

    def generate_user_id(self):
        # 获取计数器
        counter, created = UserIdCounter.objects.get_or_create(counter_name='user_id')
        new_id = counter.current_value
        counter.current_value += 1
        counter.save()
        return f"{new_id:07d}"


    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.generate_user_id()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 't_user_profile'
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"
        unique_together = ('login_id', 'login_type')


class UserEvent(models.Model):
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户唯一标识符")
    event_type = models.CharField(max_length=50, verbose_name="事件类型")
    event_data = models.TextField(verbose_name="事件数据（JSON 格式）")
    event_time = models.DateTimeField(default=now, verbose_name="事件发生时间")

    def __str__(self):
        return f"{self.user_id} - {self.event_type} - {self.event_time}"

    class Meta:
        db_table = 't_user_event'
        verbose_name = "用户事件"
        verbose_name_plural = "用户事件"
        indexes = [
            models.Index(fields=['event_time'], name='event_time_idx'),  # 为事件时间创建索引
        ]

class UserPreferences(models.Model):
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户唯一标识符")
    preference_name = models.CharField(max_length=100, verbose_name="偏好设置名称")
    preference_value = models.CharField(max_length=255, verbose_name="偏好设置值")
    created_at = models.DateTimeField(default=now, verbose_name="创建时间")

    def __str__(self):
        return f"{self.user_id} - {self.preference_name} = {self.preference_value}"

    class Meta:
        db_table = 't_user_preferences'
        verbose_name = "用户偏好设置"
        verbose_name_plural = "用户偏好设置"
        unique_together = ('user_id', 'preference_name')  # 确保每个用户的偏好设置唯一
        indexes = [
            models.Index(fields=['user_id'], name='unique_user_id_preferences_idx'),  # 修改索引名称
        ]

class UserInterests(models.Model):
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户唯一标识符")
    interest = models.CharField(max_length=100, verbose_name="用户兴趣标签")
    interest_score = models.FloatField(verbose_name="兴趣分数")
    created_at = models.DateTimeField(default=now, verbose_name="创建时间")

    def __str__(self):
        return f"{self.user_id} - {self.interest} ({self.interest_score})"

    class Meta:
        db_table = 't_user_interests'
        verbose_name = "用户兴趣标签"
        verbose_name_plural = "用户兴趣标签"
        unique_together = ('user_id', 'interest')  # 确保每个用户的兴趣标签唯一
        indexes = [
            models.Index(fields=['user_id'], name='unique_user_id_interests_idx'),  # 修改索引名称
        ]


class UserSocial(models.Model):
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_social', verbose_name="用户唯一标识符")
    friend_user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='friend_social', verbose_name="好友/关注的用户 ID")
    relationship_type = models.CharField(max_length=50, choices=[('friend', 'Friend'), ('follow', 'Follow')], verbose_name="关系类型")
    created_at = models.DateTimeField(default=now, verbose_name="创建时间")

    def __str__(self):
        return f"{self.user_id} - {self.relationship_type} - {self.friend_user_id}"

    class Meta:
        db_table = 't_user_social'
        verbose_name = "用户社交关系"
        verbose_name_plural = "用户社交关系"
        unique_together = ('user_id', 'friend_user_id', 'relationship_type')  # 确保每对用户关系唯一
        indexes = [
            models.Index(fields=['user_id'], name='user_id_social_idx'),  # 短索引名称
            models.Index(fields=['friend_user_id'], name='friend_user_id_social_idx'),  # 短索引名称
        ]


class UserActivity(models.Model):
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户唯一标识符")
    activity_type = models.CharField(max_length=50, verbose_name="活动类型", choices=[('login', 'Login'), ('logout', 'Logout')])
    activity_data = models.TextField(verbose_name="活动数据（如 IP 地址、设备信息等）")
    activity_time = models.DateTimeField(default=now, verbose_name="活动时间")

    def __str__(self):
        return f"{self.user_id} - {self.activity_type} - {self.activity_time}"

    class Meta:
        db_table = 't_user_activity'
        verbose_name = "用户活动记录"
        verbose_name_plural = "用户活动记录"
        indexes = [
            models.Index(fields=['user_id', 'activity_time'], name='user_activity_idx'),  # 组合索引
        ]

class UserTokens(models.Model):
    token_id = models.AutoField(primary_key=True, verbose_name="主键 ID")
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户唯一标识符")
    access_token = models.CharField(max_length=255, verbose_name="访问令牌 (access token)")
    refresh_token = models.CharField(max_length=255, verbose_name="刷新令牌 (refresh token)")
    token_type = models.CharField(max_length=50, verbose_name="令牌类型", default="Bearer")
    created_at = models.DateTimeField(default=now, verbose_name="令牌创建时间")
    expires_at = models.DateTimeField(verbose_name="令牌过期时间")
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="令牌最后使用时间")
    is_active = models.BooleanField(default=True, verbose_name="令牌是否有效")

    def __str__(self):
        return f"{self.user_id} - {self.token_type} - {self.access_token[:10]}"

    class Meta:
        db_table = 't_user_tokens'
        verbose_name = "用户令牌"
        verbose_name_plural = "用户令牌"


class UserSessions(models.Model):
    session_id = models.AutoField(primary_key=True, verbose_name="会话唯一标识符")
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户唯一标识符")
    session_key = models.CharField(max_length=255, verbose_name="会话密钥", unique=True)
    user_agent = models.CharField(max_length=255, verbose_name="用户的浏览器/设备信息")
    ip_address = models.CharField(max_length=45, verbose_name="用户登录时的 IP 地址")  # 支持 IPv4 和 IPv6
    last_activity = models.DateTimeField(default=now, verbose_name="最后活动时间")
    is_active = models.BooleanField(default=True, verbose_name="会话是否有效")
    created_at = models.DateTimeField(default=now, verbose_name="会话创建时间")

    def __str__(self):
        return f"{self.user_id} - {self.session_key} - {self.ip_address}"

    class Meta:
        db_table = 't_user_sessions'
        verbose_name = "用户会话"
        verbose_name_plural = "用户会话"
        indexes = [
            models.Index(fields=['user_id'], name='user_id_sessions_idx'),  # 修改索引名称
            models.Index(fields=['ip_address'], name='ip_address_sessions_idx'),  # 修改索引名称
        ]

class UserAuthLogs(models.Model):
    log_id = models.AutoField(primary_key=True, verbose_name="日志唯一标识符")
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户唯一标识符")
    action = models.CharField(max_length=50, choices=[('login', 'Login'), ('logout', 'Logout')], verbose_name="动作类型")
    timestamp = models.DateTimeField(default=now, verbose_name="发生时间")
    ip_address = models.CharField(max_length=45, verbose_name="用户登录时的 IP 地址")  # 支持 IPv4 和 IPv6
    device = models.CharField(max_length=255, verbose_name="用户登录时使用的设备信息")
    success = models.BooleanField(default=True, verbose_name="登录是否成功")

    def __str__(self):
        return f"{self.user_id} - {self.action} - {self.timestamp}"

    class Meta:
        db_table = 'user_auth_logs'
        verbose_name = "用户认证日志"
        verbose_name_plural = "用户认证日志"
        indexes = [
            models.Index(fields=['user_id', 'timestamp'], name='user_auth_logs_combined_idx'),  # 修改索引名称
        ]
