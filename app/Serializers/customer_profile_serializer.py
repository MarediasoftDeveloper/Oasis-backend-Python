from rest_framework import serializers
from app.models import Customer_profile
from app.Serializers.customer_signup_serializer import Customer_Serializer

class CustomerProfileSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True
    )

    customer = Customer_Serializer(read_only=True)
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
