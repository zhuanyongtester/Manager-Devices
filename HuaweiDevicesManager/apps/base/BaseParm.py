from django.db.models import Q
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.CustomManager.models import UserProfile, UserTokens


class BaseParm():

    def verity_access_token(self, user_id, authorization):
        if not authorization:
            raise serializers.ValidationError({"authorization": "Authorization header is missing."})
        if not authorization.startswith("Bearer "):  # 验证格式
            raise serializers.ValidationError(
                {"authorization": "Invalid authorization header format. Must start with 'Bearer '."})
        try:
            user = UserProfile.objects.get(
                Q(user_id=user_id)
            )
            getAccessToken = authorization.split(' ')[1]
            print(getAccessToken)
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
            raise ValidationError({f"user_id": f"The {user_id} doesn't exist."})
        except UserTokens.DoesNotExist:
            raise ValidationError({f"access_token is invalid."})