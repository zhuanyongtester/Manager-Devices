from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.StoresManager.storeManager.BaseStoreView import BaseStore


# Create your views here.
class StoreCreateView(BaseStore):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图

    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        data=self.store_create_status(request)
        return Response(data)

class StoreReviewView(BaseStore):
    permission_classes = [AllowAny]  # 允许任何用户访问该视图
    def post(self, request, *args, **kwargs):
        # csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        # if not csrf_token or not self.validate_csrf_token(csrf_token):
        #     return Response({"error": "CSRF token missing or invalid"}, status=status.HTTP_403_FORBIDDEN)
        data=self.store_review_status(request)


        return Response(data)