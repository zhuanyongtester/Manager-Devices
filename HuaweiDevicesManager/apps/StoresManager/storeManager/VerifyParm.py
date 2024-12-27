from django.db.models import Q
from django.utils.timezone import now
from rest_framework import status, response, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from apps.CustomManager.models import UserProfile, UserTokens
from apps.StoresManager.serializers import StoresCreateSerializer, StoreReviewCreateSerializer


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
                "errors": err_data or {}
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
            store_list = validated_data.get('store_list', [])
            return self._getSuccessRespones(self.success_1000,"verify json success",store_list)
        except Exception as e:
            return  self._getErrorRespones(500, "Error during store creation", str(e))
      return self._getErrorRespones(400, "Validation Failed", serializer.errors)

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
                "tag": stroe_tag,

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
