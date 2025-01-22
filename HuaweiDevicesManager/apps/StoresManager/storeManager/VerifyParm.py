from django.db.models import Q
from django.utils.timezone import now
from rest_framework import status, response, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from math import radians, sin, cos, sqrt, atan2

from apps.CustomManager.models import UserProfile, UserTokens
from apps.StoresManager.models import Store
from apps.StoresManager.serializers import StoresCreateSerializer, StoreReviewCreateSerializer, NearbyQuerySerializer


class VerifyParm(APIView):
    def __init__(self, error_des=None):
        self.FAILED_400 = status.HTTP_400_BAD_REQUEST
        self.SUCCESS_201= status.HTTP_201_CREATED
        self.SUCCESS_200=status.HTTP_200_OK
        self.success_1000 = 1000
        self.FAILED_1001 = 1001
        self.FAILED_1002 = 1002
        self.FAILED_1003 = 1003
        self.FAILED_1004 = 1004
        self.FAILED_CREATE = "Create Store Failed"
        self.SUCCESS_CREATE="Store Create Success"
        self.SUCCESS_CREATE_REVIEW = "Store review Success"
        self.FAILED_CREATE_REVIEW="Review Create Failed"
    def _getErrorRespones(self, result_code,message,err_data):
            response_data = {
                "statusCode": self.FAILED_400,
                "resultCode": result_code,
                "message": message,
                "data": err_data or {}
            }
            return response_data
    def _getSuccessRespones(self,result_code,message,success_data):
        response_data = {
            "statusCode": self.SUCCESS_201,
            "resultCode": result_code,
            "message": message,
            "data": success_data or {}
        }
        return response_data
    def _getStore_list(self,request):
      authorization = request.headers.get('Authorization', None)
      serializer = StoresCreateSerializer(data=request.data,context={
            'authorization': authorization})

      if  serializer.is_valid():
        print(serializer.data)
        try:
            # serializer.save()  # This triggers the create method
            validated_data = serializer.validated_data
            return self._getSuccessRespones(self.success_1000,"verify json success",validated_data)
        except Exception as e:
            return  self._getErrorRespones(500, "Error during store creation", str(e))
      return self._getErrorRespones(400, "Validation Failed", serializer.errors)
    def _nearbyQuery_save(self,data):
        new_data={
            'user':data['user_id'],
            'latitude':data['latitude'],
            'longitude':data['longitude'],
            'radius':data['radius']
        }
        serializer = NearbyQuerySerializer(data=new_data)
        success_data = []
        if serializer.is_valid():
            print("nearby ---")
            # 访问 validated_data
            print(serializer.validated_data)

            serializer.save()
            user_latitude=serializer.validated_data['latitude']
            print("nearby ---store:" + str(user_latitude))
            user_longitude = serializer.validated_data['longitude']
            radius = serializer.validated_data['radius']
            result=self._nearby_store(user_latitude,user_longitude,radius)
            for result_data in result:
                success_data.append({
                    "store_id": result_data.store_id,  # 返回 store_id
                    "store_name": result_data.store_name,  # 返回 store_name
                    "average_rating": result_data.average_rating  # 返回 average_rating
                }
                )
            return result
        else:
            # 如果序列化器无效，打印错误
           return []
    def _nearby_store(self,user_lat,user_lon,radius ):
        stores = Store.objects.all()  # 获取所有店铺

        nearby_stores = []
        for store in stores:
            store_lat = store.latitude
            store_lon = store.longitude
            distance = self.calculate_distance(user_lat, user_lon, store_lat, store_lon)

            if distance <= radius:
                nearby_stores.append(store)

        # 返回店铺信息
        return nearby_stores


    def calculate_distance(self,lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c  # Result in meters
        return distance
    def _getReviewData(self,request):
        authorization = request.headers.get('Authorization', None)
        serializer = StoreReviewCreateSerializer(data=request.data, context={
            'authorization': authorization})
        if serializer.is_valid():

            review_data={
                "store":serializer.data['store_id'],
                "user": serializer.data['user_id'],
                "rating": serializer.data['store_review']['rating'],
                "comment": serializer.data['store_review']['comment'],
            }

            stroe_tag=serializer.data['store_tag']
            tag_data={
                "store": serializer.data['store_id'],
                "user": serializer.data['user_id'],
                "tag": str(stroe_tag)

            }

            return review_data,tag_data
        else:
            return False,serializer.errors



    def verity_access_token(self,login_id,login_type,authorization):
        if not authorization:
            raise serializers.ValidationError({"authorization": "Authorization header is missing."})
        if not authorization.startswith("Bearer "):  # 验证格式
            raise serializers.ValidationError(
                {"authorization": "Invalid authorization header format. Must start with 'Bearer '."})
        try:
            user = UserProfile.objects.get(
                Q(login_id=login_id) & Q(login_type=login_type)
            )
            getAccessToken = authorization.split(' ')[1]

            user_token_content = UserTokens.objects.get(
                Q(user_id=user) & Q(access_token=getAccessToken) & Q(is_active=True)
            )
            if user_token_content.expires_at < now():
                err_data = {
                    'user_id': user.user_id,
                    "err_message": {f"access_token already Expired."}
                }
                raise ValidationError(err_data)
        except UserProfile.DoesNotExist:
            raise ValidationError({f"login_id": f"The {login_type} doesn't exist."})
        except UserTokens.DoesNotExist:
            raise ValidationError({f"access_token is invalid."})
