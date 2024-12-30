from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, response

from apps.StoresManager.models import Store
from apps.StoresManager.serializers import StoreSerializer, ReviewStoreSerializer, StoreTagSerializer, \
    StoreReviewCreateSerializer
from apps.StoresManager.storeManager.VerifyParm import VerifyParm


class BaseStore(VerifyParm):
    def store_create_status(self, request):
        result = self._getStore_list(request)

        if isinstance(result, dict) and result.get('statusCode') == 400:  # If it's a dictionary and statusCode is 400
            return result

        store_list = result.get('data', {}).get('store_list', [])  # 获取 store_list，防止键不存在的错误
        user_info = result.get('data', {}).get('user_info', None)  # 获取 user_info，若没有则为 None



        success_data = []
        failed_data = []

        for data in store_list:
            serializer = StoreSerializer(data=data)
            if serializer.is_valid():
                serializer.save()  # Save valid data
            #     success_data.append({
            #     "store_id": serializer.data["store_id"],   # 返回 store_id
            #     "store_name": serializer.data["store_name"],  # 返回 store_name
            #     "average_rating": serializer.data.get("average_rating", None)  # 返回 average_rating
            # })
            failed_data.append({
                "store_name": data.get("store_name", None),  # 返回 store_name from input data
                "address": data.get("address", None),  # 返回 store_id from input data
                "errors": serializer.errors  # Store errors for failed data
            })
        store_result=self._nearbyQuery_save(user_info)
        for result_data in store_result:
            success_data.append({
                    "store_id": result_data.store_id,  # 返回 store_id
                    "store_name":result_data.store_name,  # 返回 store_name
                    "average_rating": result_data.average_rating  # 返回 average_rating
                }
            )
        if failed_data:
            return self._getErrorRespones(
                self.FAILED_1001,
                self.FAILED_CREATE,
                {"success": success_data, "failed": failed_data}
            )

        return self._getSuccessRespones(self.success_1000, self.SUCCESS_CREATE, {"success": success_data})

    def store_review_status(self, request):
        review_data, tag_data = self._getReviewData(request)
        if not review_data:
            return self._getErrorRespones(self.FAILED_1003, self.FAILED_CREATE_REVIEW, tag_data)

        serializer = ReviewStoreSerializer(data=review_data)
        if serializer.is_valid():
            # Save the valid review data
            review_instance = serializer.save()

            # Retrieve the store ID from the saved instance
            store_id = review_instance.store_id

            # Process store tags
            data_tag = self.store_tag_status(tag_data)
            if not data_tag:
                return self._getErrorRespones(self.FAILED_1002, self.FAILED_CREATE, data_tag)

            # Retrieve the store instance and related reviews
            store_instance = get_object_or_404(Store, store_id=store_id)
            reviews = store_instance.reviews.all()
            for review in reviews:
                print(f"user name: {review.user.name}, Rating: {review.rating}, Comment: {review.comment}")

            # Update the store's average rating
            store_instance.update_average_rating()

            return self._getSuccessRespones(
                self.success_1000,
                self.SUCCESS_CREATE_REVIEW,
                serializer.data
            )

        # Handle serializer validation errors
        return self._getErrorRespones(self.FAILED_1002, self.FAILED_CREATE, serializer.errors)

    def store_tag_status(self,data):
        print("tag----")

        serializer = StoreTagSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # 保存有效的数据
            print("tag---1111")
            print(serializer.data)
            return self._getSuccessRespones(self.success_1000, self.SUCCESS_CREATE_REVIEW, serializer.data)
        print("tag----22222")
        print(serializer.errors)
        return self._getErrorRespones(self.FAILED_1002, self.FAILED_CREATE, serializer.errors)


