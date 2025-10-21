from rest_framework import serializers
from app.models import Customer_profile


class CustomerProfileSerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to return full image URL
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer_profile
        fields = [
            'id',
            'customer',
            'profile_picture',
            'profile_picture_url',
            'bio',
            'is_private',
            'total_redeemed_points',
        ]
        read_only_fields = ['customer', 'total_redeemed_points']

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None
