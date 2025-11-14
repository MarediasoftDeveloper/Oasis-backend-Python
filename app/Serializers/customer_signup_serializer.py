from rest_framework.serializers import ModelSerializer, EmailField
from rest_framework import serializers
from app.models import Customer, Customer_profile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password, check_password
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response
from rest_framework import status
from app.Models.otp_requests import OTP_Code

class Customer_Serializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    age = serializers.IntegerField(min_value=0, allow_null=True, required=False, write_only=True)
    gender = serializers.CharField(write_only=True, required=False, allow_blank=True)
    bio = serializers.CharField(write_only=True, required=False, allow_blank=True)
    profile_picture = serializers.ImageField(write_only=True, required=False, allow_null=True)
    is_private = serializers.BooleanField(write_only=True, required=False)

    def validate_email(self, value):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)


        if request and request.method == 'POST':
            customer = Customer.objects.filter(email__iexact=value).first()

            if customer:
                password_created = customer.password is not None
                if not customer.is_verified:
                    Send_Otp_Mail(customer.id)
                    raise serializers.ValidationError({
                        "verified": False,
                        "password_created": False,
                        "customer_id": customer.id,
                        "message": "Email exists but is not verified. We have sent an OTP on your email, Please verify your email."
                    })

                raise serializers.ValidationError({
                    "verified": False,
                    "password_created": password_created,
                    "error": "Email already exists."
                })

            return value  # valid new email

        if instance:
            # If the user is keeping the same email — allow it
            if instance.email.lower() == value.lower():
                return value

            # If changing to another email — make sure it's unique
            if Customer.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError("This email is already registered.")

        return value  # ensure return in all paths
                
    class Meta:
        model = Customer
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'age', 'gender',
            'bio', 'profile_picture', 'is_private'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = Customer(**validated_data)

        if password:
            instance.set_password(password)  # Hash if updated

        instance.save()
        Customer_profile.objects.get_or_create(customer=instance)
        
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        age = validated_data.pop('age', None)
        gender = validated_data.pop('gender', None)
        bio = validated_data.pop('bio', None)
        profile_picture = validated_data.pop('profile_picture', None)
        is_private = validated_data.pop('is_private', None)

            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # Hash if updated

        instance.save()
        profile = Customer_profile.objects.get(customer=instance)
        if age:
            profile.age=age 
        if gender:
            profile.gender=gender
        if bio:
            profile.bio=bio
        if profile_picture:
            profile.profile_picture=profile_picture
        if is_private is not None:
            profile.is_private=is_private
            
        profile.save()
        
        return instance