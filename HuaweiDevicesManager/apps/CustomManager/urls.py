"""
URL configuration for HuaweiDevicesManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path

from apps.CustomManager.consumers import DeviceConsumer
from apps.CustomManager.views import UserRegisterView,UserLoginView,UserLogoutView,RefreshTokenView,\
    AccessTokenView,AccountModifyView,FoundOutAccountView,GenerateQrUrlView,VerifyQrUrlView
app_name = 'DevicesManager'
urlpatterns = [
    re_path(r'^register', UserRegisterView.as_view(), name='user_register'),
    re_path(r'^login', UserLoginView.as_view(), name='user_login'),
    re_path(r'^logout', UserLogoutView.as_view(), name='user_logout'),
    re_path(r'^refresh_token', RefreshTokenView.as_view(), name='user_refresh_token'),
    re_path(r'^token', AccessTokenView.as_view(), name='user_access_token'),
    re_path(r'^modify', AccountModifyView.as_view(), name='user_modify'),
    re_path(r'^found', FoundOutAccountView.as_view(), name='user_fount_out'),
    re_path(r'^gen', GenerateQrUrlView.as_view(), name='user_generate'),
    re_path(r'^verity', VerifyQrUrlView.as_view(), name='user_verity'),

]
websocket_urlpatterns = [
    # 这里的 URL 会匹配如：/device/<device_id>/ 的 WebSocket 请求
    re_path(r'^device/(?P<session_id>[a-f0-9\-]+)/$', DeviceConsumer.as_asgi()),  # 确保路由正确
]