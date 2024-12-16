import hashlib
import uuid

from django.contrib.auth.hashers import make_password
from django.db import models

from django.utils import timezone



# Create your models here.
class CustomUser(models.Model):
    work_number = models.CharField(max_length=150, primary_key=True, verbose_name="设备唯一标识符")
    work_password = models.CharField(max_length=128)  # 密码应存储为散列值
    work_name = models.CharField(max_length=100, default="" ,verbose_name="管理员的名字")
    work_remark=models.CharField(max_length=200, default="" ,verbose_name="管理员描述")
    db_table = 't_admin_custom'  # 指定数据库表名
    def save(self, *args, **kwargs):
        # 对密码进行哈希处理
        if not self.pk:  # 只在创建新用户时哈希密码
            self.work_password = make_password(self.work_password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.work_number} - {self.work_name}"
class Token(models.Model):
    work_person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, unique=True)
    fresh_token=models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 't_admin_token'  # 指定数据库表名
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @classmethod
    def generate_access_token(cls, user):
        unique_string = f"{user.work_number}{user.work_password}{timezone.now()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()

    @classmethod
    def generate_refresh_token(cls, user):
        unique_string = f"{user.work_number}{user.work_password}{uuid.uuid4()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()