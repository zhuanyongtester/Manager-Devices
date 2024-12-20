from rest_framework.views import APIView


class AccountUserManager(APIView):
    def generate_user_id(self):
        import uuid
        return str(uuid.uuid4())[:8]  # 生成 8 位的唯一 ID