from django.contrib import admin
from apps.CustomManager.models import UserProfile,UserEvent,UserInterests,UserPreferences,UserSocial,\
     UserActivity,UserTokens,UserSessions,UserAuthLogs
# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'gender', 'age', 'location', 'login_id', 'created_at', 'updated_at')
    search_fields = ('name', 'login_id', 'location')
    list_filter = ('gender', 'language', 'login_type')

@admin.register(UserEvent)
class UserEventAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'event_type', 'event_time')
    search_fields = ('user_profile__name', 'event_type')  # 支持按用户姓名或事件类型搜索
    list_filter = ('event_type', 'event_time')      # 提供事件类型和时间的过滤功能

@admin.register(UserInterests)
class UserInterestsAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'interest', 'interest_score', 'created_at')
    search_fields = ('user_profile__name', 'interest')  # 支持按用户姓名或兴趣标签搜索
    list_filter = ('interest', 'created_at')      # 提供兴趣和时间的过滤功能

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'preference_name', 'preference_value', 'created_at')
    search_fields = ('user_profile__name', 'preference_name')  # 支持按用户姓名或偏好名称搜索
    list_filter = ('preference_name', 'created_at')  # 提供偏好名称和时间的过滤功'

@admin.register(UserSocial)
class UserSocialAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'friend_user_id', 'relationship_type', 'created_at')
    search_fields = ('user_profile__name', 'friend_user_id__name', 'relationship_type')  # 支持搜索
    list_filter = ('relationship_type', 'created_at')

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'activity_type', 'activity_time')
    search_fields = ('user_profile__name', 'activity_type')  # 按用户名称或活动类型搜索
    list_filter = ('activity_type', 'activity_time')  # 过滤活动类型和时间

@admin.register(UserTokens)
class UserTokensAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'token_type', 'access_token', 'expires_at', 'created_at', 'is_active')
    search_fields = ('user_profile', 'access_token', 'refresh_token')  # 支持按用户 ID、访问令牌、刷新令牌搜索
    list_filter = ('token_type', 'is_active', 'created_at')  # 过滤功能

@admin.register(UserSessions)
class UserSessionsAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'session_key', 'ip_address', 'last_activity', 'is_active', 'created_at')
    search_fields = ('user_profile__name', 'session_key', 'ip_address')  # 支持搜索
    list_filter = ('is_active', 'created_at', 'ip_address')
@admin.register(UserAuthLogs)
class UserAuthLogsAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'action', 'ip_address', 'timestamp', 'success')
    search_fields = ('user_profile__name', 'action', 'ip_address')  # 支持搜索
    list_filter = ('action', 'timestamp', 'success')  # 过