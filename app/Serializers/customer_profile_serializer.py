from rest_framework import serializers
from app.models import Customer_profile
from app.Serializers.customer_signup_serializer import Customer_Serializer

class CustomerProfileSerializer(serializers.ModelSerializer):
    # profile_picture_url = serializers.SerializerMethodField(read_only=True)
    customer = Customer_Serializer()
    class Meta:
        model = Customer_profile
        fields = [
            'customer',
            'profile_picture',
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
