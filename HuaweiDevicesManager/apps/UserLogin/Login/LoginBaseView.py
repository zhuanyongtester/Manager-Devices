import hashlib
import json
import uuid

import pytz
from django.contrib.auth.hashers import check_password
from django.db.models.functions import SHA256
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from apps.UserLogin.models import CustomUser, Token
from datetime import timedelta


from django.views import View

class BaseView(View):

    def getAdminName(self,request):
        try:
            work_name = request.session.get('work_name')  # 获取 URL 中的 work_name
            user = CustomUser.objects.get(work_number=work_name)  # 根据 work_number 查询用户
            return user.work_name  # 返回工作名称
        except CustomUser.DoesNotExist:
            return None  # 用户不存在时返回 None


    def authAccount(self,request):
        if not request.body:
            return JsonResponse({"success": False, "message": "请求体为空"})

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as e:
            return JsonResponse({"success": False, "message": "JSON 解码错误", "error": str(e)})

        work_name = data.get('work_name')
        work_password = data.get('work_password')
        print(str(work_name)+"-ssss--"+str(work_password))

        # 查询用户
        try:
            user = CustomUser.objects.get(work_number=work_name)
            password=user.work_number+user.work_password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(hashed_password)
            if work_password==hashed_password:  # 验证密码
                # 生成 access_token 和 refresh_token
                request.session['work_name'] = work_name  # 存储 work_name 到会话中
                access_token = Token.generate_access_token(user)
                refresh_token = Token.generate_refresh_token(user)
                request.session['access_token'] = access_token  # 存储 work_name 到会话中
                # 设置 token 的过期时间
                expires_at = timezone.now() + timedelta(hours=1)  # 1小时后过期

                # 保存 token
                token = Token.objects.create(
                    work_person=user,
                    access_token=access_token,
                    fresh_token=refresh_token,
                    expires_at=expires_at
                )

                return JsonResponse({
                    "success": True,
                    "message": "登录成功",
                    "access_token": token.access_token,
                    "refresh_token": token.fresh_token,
                })
            else:
                return JsonResponse({"success": False, "message": "密码错误"})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "message": "用户不存在"})

    @csrf_exempt
    def refresh_token_view(self, request):
        if request.method == "POST":
            data = json.loads(request.body)
            refresh_token = data.get('refresh_token')

            # 验证 refresh token
            try:
                token = Token.objects.get(fresh_token=refresh_token)

                # 生成新的 access_token
                new_access_token = str(uuid.uuid4())
                token.access_token = new_access_token  # 更新 access_token
                token.expires_at = timezone.now() + timedelta(hours=1)  # 更新过期时间
                token.save()

                return JsonResponse({
                    "success": True,
                    "message": "Token 刷新成功",
                    "access_token": new_access_token
                })
            except Token.DoesNotExist:
                return JsonResponse({"success": False, "message": "无效的 token"})
        return JsonResponse({"success": False, "message": "无效的请求"})

    @csrf_exempt
    def protected_view(self, request):
        if request.method == "GET":
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header:
                token = auth_header.split(' ')[1]  # 获取 token

                try:
                    token_obj = Token.objects.get(access_token=token)
                    if token_obj.is_expired():
                        return JsonResponse({"success": False, "message": "Token 已过期"}, status=401)

                    return JsonResponse(
                        {"success": True, "message": "访问成功", "user": token_obj.work_person.work_name})

                except Token.DoesNotExist:
                    return JsonResponse({"success": False, "message": "无效的 token"}, status=401)

            return JsonResponse({"success": False, "message": "缺少认证 token"}, status=401)
    def accountShow(self,request):
        work_name = request.session.get('work_name')

        access_token = request.session.get('access_token')
        try:
            token = Token.objects.filter(access_token=access_token).first()

            created_at_plus_8 = token.created_at  + timedelta(hours=8)
            jsonUserData={
                "work_name":token.work_person.work_name,
                "admin_job":token.work_person.work_number,
                "admin_love":token.work_person.work_remark,
                "admin_time":created_at_plus_8
            }
        except Token.DoesNotExist:
            jsonUserData={}
        return jsonUserData


    def autAccessToken(self,request):
        work_name = request.session.get('work_name')
        access_token = request.session.get('access_token')
        print(access_token)
        if not access_token:
            return JsonResponse({'success': False, 'message': '未找到访问令牌'}, status=404)

        # 查询数据库中的该 access_token
        token = Token.objects.filter(access_token=access_token).first()
        user_name=token.work_person.work_number
        if not token or token.is_expired():
            return JsonResponse({'success': False, 'message': '令牌无效或已过期'}, status=404)
        if work_name!=user_name:
            return JsonResponse({'success': False, 'message': '令牌无效或已过期'}, status=404)
        # 将过期时间设置为当前时间，立即失效
        token.expires_at = timezone.now()
        token.save()

        # 日志记录用户登出事件
        # logger.info(f"用户 {request.user.username} 已登出，令牌 {access_token} 被标记为过期。")

        return JsonResponse({'success': True, 'message': '成功退出'})