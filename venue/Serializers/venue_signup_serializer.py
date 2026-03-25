from rest_framework.serializers import ModelSerializer, EmailField
from rest_framework import serializers
from app.models import Customer
from app.Serializers.customer_signup_serializer import Customer_Serializer
from venue.models.venue_info import Venue_Info
from venue.models.venue_opening_hours import Venue_Opening_Hours
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password, check_password
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response
from django.contrib.auth.models import User



class Venue_SignUp_Serializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    venue_name = serializers.CharField(write_only=True, required=True)
    

    
    def validate_username(self, value):
        """Ensure the username is unique."""
        if Customer.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError({"message": "Username already exists."})
        return value

    def validate_email(self, value):
        """Ensure the email is unique and handle unverified emails."""
        if Customer.objects.filter(email__iexact=value).exists():
            customer = Customer.objects.get(email__iexact=value)
            if not customer.is_verified:
                Send_Otp_Mail(customer.id)  # Send OTP if email is unverified
                raise serializers.ValidationError({
                    "code": "unverified_email",
                    "message": "Email exists but is not verified. We have sent an OTP to your email, Please verify it."
                })
            raise serializers.ValidationError({"message": "Oasis account with this email already exists. Please login"})

        return value  # If email is unique

    
                
    class Meta:
        model = Customer
        fields = ['id','username', 'email', 'password', 'venue_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        venue_name = validated_data.pop('venue_name')
        instance = Customer(**validated_data)

        if password:
            instance.set_password(password)  # Hash if updated
            instance.user_role = '2'  # user role set to venue
        instance.save()
        time_not_set = "Not Set"
        venue_profile = Venue_Info.objects.create(venue=instance, venue_name=venue_name)
        opening_hours = Venue_Opening_Hours.objects.create(venue=instance, monday=time_not_set, tuesday=time_not_set, wednesday=time_not_set, thursday=time_not_set, friday=time_not_set,saturday=time_not_set,sunday=time_not_set)
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Hash if updated
        instance.save()
        return instance
    




class Venue_SignUp_Serializer_Staff(ModelSerializer):
                
    class Meta:
        model = Customer
        fields = ['id','username', 'date_joined']
