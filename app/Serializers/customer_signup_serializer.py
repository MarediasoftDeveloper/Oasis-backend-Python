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

    def validate_email(self, value):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)


        if request and request.method == 'POST':
            customer = Customer.objects.filter(email__iexact=value).first()

            if customer:
                if not customer.is_verified:
                    Send_Otp_Mail(customer.id)
                    raise serializers.ValidationError({
                        "code": "unverified_email",
                        "customer_id": customer.id,
                        "message": "Email exists but is not verified. We have sent an OTP on your email, Please verify your email."
                    })
                raise serializers.ValidationError("Email already exists.")

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
        fields = ['id','username', 'email', 'password', 'first_name', 'last_name', 'age', 'gender']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = Customer(**validated_data)

        if password:
            instance.set_password(password)  # Hash if updated

        instance.save()
        customer_profile, _ = Customer_profile.objects.get_or_create(customer=instance)
        
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        age = validated_data.pop('age', None)
        gender = validated_data.pop('gender', None)

            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # Hash if updated

        instance.save()
        if age or gender:
            customer_profile = Customer_profile.objects.get(customer=instance)
            customer_profile.age=age 
            customer_profile.gender=gender
            customer_profile.save()
        
        return instance