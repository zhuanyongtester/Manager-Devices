from rest_framework import serializers
from .models import Store, StoreTag, Review


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'store_id',
            'store_name', 'district_code', 'address', 'phone_number',
                  'latitude', 'longitude',
                  'category', 'average_rating', 'price_range', 'opening_hours']
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
    login_id = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Login ID of the user creating the stores."
    )
    # class Meta:
    #
    #     fields = ['create_store', 'store_list', 'login_id']

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

    def validate_login_id(self, value):
        """Ensure 'login_id' is provided."""
        if not value.strip():
            raise serializers.ValidationError("The 'login_id' field is required and cannot be blank.")
        return value

    def validate(self, attrs):
        """Perform cross-field validation."""
        if attrs.get('create_store') == 'create' and not attrs.get('store_list'):
            raise serializers.ValidationError("When 'create_store' is 'create', 'store_list' cannot be empty.")
        return attrs

    def create(self, validated_data):
        """
            批量创建 store_List 中的所有店铺信息。
            """
        store_data_list = validated_data.get('store_List')
        stores = [StoreSerializer(data=data).create(data) for data in store_data_list]
        return stores

class StoreTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTag
        fields = [ 'store','user', 'tag', 'created_at']
    def validate_store(self,value):
        if not value:
            raise serializers.ValidationError("Store Id is required and cannot be empty.")
        return value
    def validate_tag(self,value):
        if not value.strip():
            raise serializers.ValidationError("tag required and cannot be empty.")
        return value



class ReviewStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['store', 'user', 'rating', 'comment','created_at']

    def validate_store(self,value):
        if not value:
            raise serializers.ValidationError("Store Id is required and cannot be empty.")
        return value
    def validate_user(self,value):
        if not value:
            raise serializers.ValidationError("user Id is required and cannot be empty.")
        return value