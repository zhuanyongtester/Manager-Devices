from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, response

from apps.StoresManager.models import Store
from apps.StoresManager.serializers import StoreSerializer, ReviewStoreSerializer, StoreTagSerializer
from apps.StoresManager.storeManager.VerifyParm import VerifyParm


class BaseStore(VerifyParm):
    def store_create_status(self, request):
        result = self._getStore_list(request)

        if isinstance(result, dict) and result.get('statusCode') == 400:  # If it's a dictionary and statusCode is 400
            return result

        success_data = []
        failed_data = []

        for data in result['data']:
            serializer = StoreSerializer(data=data)
            if serializer.is_valid():
                serializer.save()  # Save valid data
                success_data.append({
                "store_id": serializer.data["store_id"],   # 返回 store_id
                "store_name": serializer.data["store_name"],  # 返回 store_name
                "average_rating": serializer.data.get("average_rating", None)  # 返回 average_rating
            })
            failed_data.append({
                "store_name": data.get("store_name", None),  # 返回 store_name from input data
                "address": data.get("address", None),  # 返回 store_id from input data
                "errors": serializer.errors  # Store errors for failed data
            })

        if failed_data:
            return self._getErrorRespones(
                self.FAILED_1001,
                self.FAILED_CREATE,
                {"success": success_data, "failed": failed_data}
            )

        return self._getSuccessRespones(self.success_1000, self.SUCCESS_CREATE, {"success": success_data})

    def store_review_status(self,request):
        serializer = ReviewStoreSerializer(data=request.data)
        store_id=request.data['store']
        if serializer.is_valid():
            data_tag = self.store_tag_status(request)
            if not data_tag:
                return self._getErrorRespones(self.FAILED_1002, self.FAILED_CREATE, data_tag)
            store_instance = Store.objects.get(store_id=store_id)
            reviews = store_instance.reviews.all()  # 使用 related_name 访问评论
            for review in reviews:
                print(f"user name: {review.user.name},Rating: {review.rating}, Comment: {review.comment}")
            store = get_object_or_404(Store,store_id=store_id)
            store.update_average_rating()  # 更新评分
            serializer.save()  # 保存有效的数据

            return self._getSuccessRespones(self.success_1000, self.SUCCESS_CREATE_REVIEW, serializer.data)
        return self._getErrorRespones(self.FAILED_1002, self.FAILED_CREATE, serializer.errors)

    def store_tag_status(self,request):
        serializer = StoreTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 保存有效的数据
            return self._getSuccessRespones(self.success_1000, self.SUCCESS_CREATE_REVIEW, serializer.data)
        return self._getErrorRespones(self.FAILED_1002, self.FAILED_CREATE, serializer.errors)


