import re
from datetime import datetime
from idlelib.textview import ViewWindow
from urllib import request

from rest_framework import status, response

from rest_framework.views import APIView

from apps.CustomManager import views
from apps.CustomManager.models import UserProfile


class AccessAuth(APIView):
    def registerStatus(self, request):
        # 必须字段检查
        required_fields = ['login_id', 'password', 'name', 'gender', 'birthday', 'location', 'age', 'language',
                           'login_type']
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return self._error_response(2001, "User registration failed due to missing fields", missing_fields)

        # 参数不能为空检查
        for field in required_fields:
            value = request.data.get(field, None)  # 获取字段值
            if isinstance(value, str):
                value = value.strip()
            if not value:
                return self._error_response(2002,
                                            f"{field.replace('_', ' ').capitalize()} is required and cannot be empty",
                                            [field])

        # 登录类型检查
        login_type = request.data['login_type']
        if login_type not in ['email', 'phone']:
            return self._error_response(2003, "Invalid login type",
                                        {"login_type": "Invalid login type. Must be 'email' or 'phone'."})

        login_id = request.data['login_id']

        if login_type == 'email':
            email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
            if not re.match(email_pattern, login_id):
                return self._error_response(2004, "Invalid email format", {"login_id": "Invalid email format."})

        elif login_type == 'phone':
            phone_pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
            if not re.match(phone_pattern, login_id):
                return self._error_response(2004, "Invalid phone number format",
                                            {"login_id": "Invalid phone number format."})

        # 检查 login_id 和 login_type 是否已存在
        if UserProfile.objects.filter(login_id=login_id, login_type=login_type).exists():
            return self._error_response(2005, f"{login_id} already exists", {"login_id": f"{login_id} already exists"})

        # 验证其他字段
        name = request.data['name'].strip()
        if not name:
            return self._error_response(2004, "Name is required and cannot be empty",
                                        {"name": "Name is required and cannot be empty"})

        gender = request.data['gender']
        if gender not in ['male', 'female', 'other']:
            return self._error_response(2004, "Invalid gender",
                                        {"gender": "please choose gender (male, female, or other)"})

        birthday = request.data['birthday']
        if not self.validate_birthday(birthday):
            return self._error_response(2004, "Invalid birthday format or date",
                                        {"birthday": "Invalid birthday format or date"})

        location = request.data['location'].strip()
        if not location:
            return self._error_response(2004, "Location is required and cannot be empty",
                                        {"location": "Location is required and cannot be empty"})

        age = request.data['age']
        try:
            age = int(age)
            if age < 0:
                raise ValueError()
        except ValueError:
            return self._error_response(2004, "Invalid age", {"age": "Age must be a positive integer"})

        language = request.data['language'].strip()
        if not language:
            return self._error_response(2012, "Language is required and cannot be empty",
                                        {"language": "Language is required and cannot be empty"})

    def validate_birthday(self, birthday):
        try:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            return birth_date < datetime.now()  # 确保出生日期小于当前日期
        except ValueError:
            return False

    def _error_response(self, result_code, message, errors=None):
        response_data = {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "resultCode": result_code,
            "message": message,
            "errors": errors or {}
        }
        return response.Response(response_data, status=status.HTTP_400_BAD_REQUEST)
