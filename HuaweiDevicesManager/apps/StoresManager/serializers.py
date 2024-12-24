from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['store_id', 'store_name', 'district_code', 'address', 'phone_number', 'latitude', 'longitude',
                  'category', 'rating', 'price_range', 'opening_hours']
        read_only_fields = ['store_id']  # 这个字段不允许修改，Django会自动生成

    def validate_store_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Store name is required and cannot be empty.")
        return value

    def validate_district_code(self, value):
        if not value.strip():
            raise serializers.ValidationError("District code is required and cannot be empty.")
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
        """
        在这里执行跨字段的验证，确保区号唯一性。
        """
        district_code = data.get('district_code')

        # 验证区号是否已经存在
        if Store.objects.filter(district_code=district_code).exists():
            raise serializers.ValidationError(f"A store with district code {district_code} already exists.")

        # 地址和经纬度的一致性检查
        address = data.get('address')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # 你可以根据实际需求增加更多的跨字段验证
        if not address or not latitude or not longitude:
            raise serializers.ValidationError("Address, latitude, and longitude must be provided together.")

        return data