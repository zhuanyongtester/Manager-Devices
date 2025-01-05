from django.db.models import Q
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Store, StoreTag, Review, NearbyQuery, StoreImage
from ..CustomManager.models import UserProfile, UserTokens
from ..base.BaseParm import BaseParm

class StoreImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreImage
        fields = ['store_id',
            'image_url', 'image_type', 'created_at']
class StoreSerializer(serializers.ModelSerializer):
    store_image = StoreImageSerializer(many=True, read_only=True)  # 使用 related_name 'images'

    class Meta:
        model = Store
        fields = [
            'store_id',
            'store_name', 'district_code', 'address', 'phone_number',
                  'latitude', 'longitude',
                  'category', 'average_rating', 'price_range', 'opening_hours',
                  'store_image']
        read_only_fields = ['store_id']  # 这个字段不允许修改，Django会自动生成

    def validate_store_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Store name is required and cannot be empty.")
        return value
    def validate_district_code(self,value):
        if not value:
            raise serializers.ValidationError("district code is required and cannot be empty.")
            # 检查是否为整数
        if not isinstance(value, int):
            raise serializers.ValidationError("District code must be an integer.")

            # 可选：检查整数的范围
        if value < 1000 or value > 99999:  # 假设区号为 4 位整数
            raise serializers.ValidationError("District code must be a 5-digit integer.")

        if Store.objects.filter(district_code=value).exists():
            raise serializers.ValidationError(f"A store with district code {value} already exists.")

        return value
    def validate_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Address is required and cannot be empty.")
        return value

    def validate_phone_number(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError("Phone number should be at least 10 digits.")
        return value

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate(self, data):

        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if Store.objects.filter( latitude=latitude,longitude=longitude).exists():
            raise serializers.ValidationError(f"A store location already exists.")

        return data
    def create(self, validated_data):
        store_images_data = validated_data.pop('store_image', [])  # 提取关联的 store_image 数据
        store = Store.objects.create(**validated_data)
        for image_data in store_images_data:
            StoreImage.objects.create(store=store, **image_data)
        return store
class StoresCreateSerializer(serializers.Serializer):

    create_store = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="This field must contain the string 'create'."
    )
    store_list = serializers.ListField(
        child=serializers.DictField(),  # 允许字典对象作为项
        required=True,
        help_text="A list of store dictionaries. Each item should be a dictionary."
    )
    user_info = serializers.DictField(
        required=True,
        help_text="User information including user_id, latitude, and longitude.",
    )


    def validate_create_store(self, value):
        """Ensure 'create_store' is set to 'create'."""
        if value != "create":
            raise serializers.ValidationError("The 'create_store' field must be 'create'.")
        return value

    def validate_store_list(self, value):
        """Validate that 'store_list' is a non-empty list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("The 'store_list' field must be a list.")
        if not value:
            raise serializers.ValidationError("The 'store_list' field cannot be empty.")
        # Optionally validate individual items in the list
        # for store in value:
        #     if not isinstance(store, str):
        #         raise serializers.ValidationError("Each item in 'store_list' must be a string.")
        return value

    def validate(self, attrs):
        """Perform cross-field validation."""
        authorization = self.context.get('authorization')  # 从 context 中获取 Authorization
        user_info = attrs.get('user_info')
        user_id = user_info.get('user_id') if user_info else None

        baseParm = BaseParm()
        baseParm.verity_access_token(user_id,authorization)
        if attrs.get('create_store') == 'create' and not attrs.get('store_list'):
            raise serializers.ValidationError("When 'create_store' is 'create', 'store_list' cannot be empty.")
        latitude = user_info.get('latitude')
        longitude = user_info.get('longitude')
        if not latitude or not longitude:
            raise serializers.ValidationError("Latitude and longitude are required in user_info.")
        radius = user_info.get('radius')
        if not radius:
            raise serializers.ValidationError("Radius are required in user_info.")
        return attrs

    def create(self, validated_data):
        """
            批量创建 store_List 中的所有店铺信息。
            """
        store_data_list = validated_data.get('store_List')
        stores = [StoreSerializer(data=data).create(data) for data in store_data_list]
        return stores
from rest_framework import serializers


class StoreReviewCreateSerializer(serializers.Serializer):
    store_type = serializers.ChoiceField(
        choices=["review"],
        required=True,
        help_text="The type of store interaction, e.g., 'review'."
    )
    store_id = serializers.CharField(
        required=True,
        max_length=15,
        help_text="The unique ID of the store."
    )
    user_id = serializers.CharField(
        required=True,
        max_length=15,
        help_text="The unique ID of the user making the interaction."
    )
    store_review = serializers.JSONField(
        required=True,
        help_text="Details of the store review."
    )
    store_tag = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False,
        help_text="Overall tags associated with the store."
    )

    def validate_store_review(self, value):
        """
        Validate the structure and content of `store_review`.
        """
        required_fields = {"review_id", "rating", "comment", "timestamp"}
        if isinstance(value, dict):
            missing_fields = required_fields - set(value.keys())
        else:
            raise serializers.ValidationError("Expected a dictionary, but got a list or another type.")
        if missing_fields:
            raise serializers.ValidationError(
                f"Missing required fields in store_review: {', '.join(missing_fields)}"
            )

        # Validate individual fields
        rating = value.get("rating")
        if not (1 <= rating <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")

        timestamp = value.get("timestamp")
        try:
            from datetime import datetime
            datetime.fromisoformat(timestamp)
        except ValueError:
            raise serializers.ValidationError("Timestamp must be in ISO 8601 format.")

        return value

    def validate_store_tag(self, value):
        """
        Validate `store_tag` to ensure it is a list of unique non-empty strings.
        """
        if not all(isinstance(tag, str) and tag.strip() for tag in value):
            raise serializers.ValidationError("All tags must be non-empty strings.")

        # Ensure tags are unique
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Tags must be unique.")

        return value

    def validate(self, attrs):
        """
        Cross-field validation for store_id, user_id, and store_type.
        """
        authorization = self.context.get('authorization')
        user_id = attrs.get('user_id')
        store_type = attrs.get("store_type")
        store_id = attrs.get("store_id")

        baseParm = BaseParm()
        baseParm.verity_access_token(user_id, authorization)


        if store_type != "review":
            raise serializers.ValidationError("Currently, only 'review' store_type is supported.")
        try:
            Store.objects.get(Q(store_id=store_id))
        except Store.DoesNotExist:
            raise ValidationError({f"store_id": f"The {store_id} doesn't exist."})
        # Add additional cross-field validation if needed
        # 如果 store_tag 不存在或者为空，赋予默认空列表

        store_review = attrs.get("store_review", {})
        store_tag = attrs.get("store_tag", [])
        if store_tag is None:
            store_tag = []
        # 从 store_review 中提取 tag
        review_tag = store_review.get("tag", "").strip("[]")  # 去掉方括号

        # 如果 review_tag 不在 store_tag 中，加入 store_tag
        if review_tag and review_tag not in store_tag:
            store_tag.append(review_tag)

        # 更新 store_tag 回到 attrs
        attrs["store_tag"] = store_tag
        return attrs


class StoreTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTag
        fields = ['store', 'user', 'tag', 'created_at']

    def validate_store(self, value):
        if not value:
            raise serializers.ValidationError("Store ID is required and cannot be empty.")
        return value

    def validate_tag(self, value):
        if not value.strip():
            raise serializers.ValidationError("Tag is required and cannot be empty.")
        return value

    def create(self, validated_data):
        user = StoreTag.objects.create(**validated_data)
        user.save()
        return user


class ReviewStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['store', 'user', 'rating', 'comment', 'created_at']

    def validate_store_id(self, value):
        if not value:
            raise serializers.ValidationError("Store ID is required and cannot be empty.")
        return value

    def validate_user_id(self, value):
        if not value:
            raise serializers.ValidationError("User ID is required and cannot be empty.")
        return value

    def validate(self, attrs):
        # Perform cross-field validation
        store = attrs.get('store')
        user = attrs.get('user')
        rating = attrs.get('rating')

        if not (store and user and rating):
            raise serializers.ValidationError("Store, User, and Rating are mandatory fields.")
        return attrs

    def create(self, validated_data):
        user = Review.objects.create(**validated_data)
        user.save()
        return user


class NearbyQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = NearbyQuery  # 序列化器使用的模型是 NearbyQuery
        fields = ['user', 'latitude', 'longitude', 'radius', 'created_at']  # 序列化的字段
        read_only_fields = ['created_at']  # created_at 字段是只读的，不允许通过请求数据传入

    def validate(self, attrs):
        """
        可以在这里添加验证逻辑，如果需要对用户提交的查询数据进行额外的校验，可以在这里添加。
        """
        # 示例：确保 radius 大于 0

        if attrs.get('radius', 0) <= 0:
            raise serializers.ValidationError("Radius must be greater than 0.")
        return attrs

    def create(self, validated_data):
        user = NearbyQuery.objects.create(**validated_data)
        return user

