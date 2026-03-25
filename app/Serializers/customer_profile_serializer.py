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



class CustomerProfileSerializerStaff(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    
    
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
            'age',
            'gender',
            'username',
            'first_name',
            'last_name',
            'email',
            'total_redeemed_points',
        ]
        read_only_fields = ['customer', 'total_redeemed_points',  'username',
            'first_name',
            'last_name',
            'email',]


    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None


    def update(self, instance, validated_data):
        
        username = validated_data.pop('username')
        firstname = validated_data.pop('first_name')
        lastname = validated_data.pop('last_name')
        email = validated_data.pop('email')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if username:
            instance.customer.username=username
        if firstname:
            instance.customer.first_name=firstname
        if lastname:
            instance.customer.last_name=lastname
        if email:
            instance.customer.email=email
        instance.customer.save()
        
        instance.save()

        
        return instance