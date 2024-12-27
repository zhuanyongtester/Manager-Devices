# Generated by Django 5.1.4 on 2024-12-27 03:46

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserIdCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter_name', models.CharField(max_length=50, unique=True)),
                ('current_value', models.PositiveIntegerField(default=1000000)),
            ],
            options={
                'verbose_name': '用户资料',
                'db_table': 't_user_id_counter',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user_id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True, verbose_name='用户唯一标识符')),
                ('name', models.CharField(max_length=100, verbose_name='用户姓名')),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=10, verbose_name='性别')),
                ('age', models.IntegerField(verbose_name='年龄')),
                ('birthday', models.DateField(verbose_name='出生日期')),
                ('location', models.CharField(max_length=255, verbose_name='用户所在位置')),
                ('profession', models.CharField(max_length=100, verbose_name='职业')),
                ('language', models.CharField(max_length=10, verbose_name='语言偏好')),
                ('login_id', models.CharField(max_length=255, unique=True, verbose_name='用户邮箱或手机号')),
                ('login_type', models.CharField(choices=[('email', 'Email'), ('phone', 'Phone')], max_length=10, verbose_name='用户注册方式')),
                ('password', models.CharField(max_length=255, verbose_name='用户密码')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='账户创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='账户信息更新时间')),
            ],
            options={
                'verbose_name': '用户资料',
                'verbose_name_plural': '用户资料',
                'db_table': 't_user_profile',
                'unique_together': {('login_id', 'login_type')},
            },
        ),
        migrations.CreateModel(
            name='UserTokens',
            fields=[
                ('token_id', models.AutoField(primary_key=True, serialize=False, verbose_name='主键 ID')),
                ('access_token', models.CharField(max_length=255, verbose_name='访问令牌 (access token)')),
                ('refresh_token', models.CharField(max_length=255, verbose_name='刷新令牌 (refresh token)')),
                ('token_type', models.CharField(default='Bearer', max_length=50, verbose_name='令牌类型')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='令牌创建时间')),
                ('expires_at', models.DateTimeField(verbose_name='令牌过期时间')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='令牌最后使用时间')),
                ('is_active', models.BooleanField(default=True, verbose_name='令牌是否有效')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户令牌',
                'verbose_name_plural': '用户令牌',
                'db_table': 't_user_tokens',
            },
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference_name', models.CharField(max_length=100, verbose_name='偏好设置名称')),
                ('preference_value', models.CharField(max_length=255, verbose_name='偏好设置值')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户偏好设置',
                'verbose_name_plural': '用户偏好设置',
                'db_table': 't_user_preferences',
                'indexes': [models.Index(fields=['user_id'], name='unique_user_id_preferences_idx')],
                'unique_together': {('user_id', 'preference_name')},
            },
        ),
        migrations.CreateModel(
            name='UserInterests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.CharField(max_length=100, verbose_name='用户兴趣标签')),
                ('interest_score', models.FloatField(verbose_name='兴趣分数')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户兴趣标签',
                'verbose_name_plural': '用户兴趣标签',
                'db_table': 't_user_interests',
                'indexes': [models.Index(fields=['user_id'], name='unique_user_id_interests_idx')],
                'unique_together': {('user_id', 'interest')},
            },
        ),
        migrations.CreateModel(
            name='UserEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=50, verbose_name='事件类型')),
                ('event_data', models.TextField(verbose_name='事件数据（JSON 格式）')),
                ('event_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='事件发生时间')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户事件',
                'verbose_name_plural': '用户事件',
                'db_table': 't_user_event',
                'indexes': [models.Index(fields=['event_time'], name='event_time_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserAuthLogs',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False, verbose_name='日志唯一标识符')),
                ('action', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('token', 'Token'), ('refresh', 'Refresh')], max_length=50, verbose_name='动作类型')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='发生时间')),
                ('ip_address', models.CharField(max_length=45, verbose_name='用户登录时的 IP 地址')),
                ('device', models.CharField(max_length=255, verbose_name='用户登录时使用的设备信息')),
                ('success', models.BooleanField(default=True, verbose_name='登录是否成功')),
                ('failure_reason', models.TextField(blank=True, null=True, verbose_name='失败原因')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户认证日志',
                'verbose_name_plural': '用户认证日志',
                'db_table': 'user_auth_logs',
                'indexes': [models.Index(fields=['user_id', 'timestamp'], name='user_auth_logs_combined_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout')], max_length=50, verbose_name='活动类型')),
                ('activity_data', models.TextField(verbose_name='活动数据（如 IP 地址、设备信息等）')),
                ('activity_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='活动时间')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户活动记录',
                'verbose_name_plural': '用户活动记录',
                'db_table': 't_user_activity',
                'indexes': [models.Index(fields=['user_id', 'activity_time'], name='user_activity_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserSessions',
            fields=[
                ('session_id', models.AutoField(primary_key=True, serialize=False, verbose_name='会话唯一标识符')),
                ('session_key', models.CharField(max_length=255, unique=True, verbose_name='会话密钥')),
                ('user_agent', models.CharField(max_length=255, verbose_name='用户的浏览器/设备信息')),
                ('ip_address', models.CharField(max_length=45, verbose_name='用户登录时的 IP 地址')),
                ('login_method', models.CharField(choices=[('password', 'Password'), ('token', 'Token')], default='password', max_length=20, verbose_name='登录方式')),
                ('last_activity', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后活动时间')),
                ('is_active', models.BooleanField(default=True, verbose_name='会话是否有效')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='会话创建时间')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户会话',
                'verbose_name_plural': '用户会话',
                'db_table': 't_user_sessions',
                'indexes': [models.Index(fields=['user_id'], name='user_id_sessions_idx'), models.Index(fields=['ip_address'], name='ip_address_sessions_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_type', models.CharField(choices=[('friend', 'Friend'), ('follow', 'Follow')], max_length=50, verbose_name='关系类型')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('friend_user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_social', to='CustomManager.userprofile', verbose_name='好友/关注的用户 ID')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_social', to='CustomManager.userprofile', verbose_name='用户唯一标识符')),
            ],
            options={
                'verbose_name': '用户社交关系',
                'verbose_name_plural': '用户社交关系',
                'db_table': 't_user_social',
                'indexes': [models.Index(fields=['user_id'], name='user_id_social_idx'), models.Index(fields=['friend_user_id'], name='friend_user_id_social_idx')],
                'unique_together': {('user_id', 'friend_user_id', 'relationship_type')},
            },
        ),
    ]
