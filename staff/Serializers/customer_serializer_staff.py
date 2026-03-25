from rest_framework.serializers import ModelSerializer, EmailField
from rest_framework import serializers
from app.models import Customer, Customer_profile
from venue.models.venue_info import Venue_Info
from venue.models.venue_opening_hours import Venue_Opening_Hours
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password, check_password
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response
from rest_framework import status
from app.Models.otp_requests import OTP_Code

class Customer_Serializer_Staff(ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    venue_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    venue_logo = serializers.ImageField(write_only=True, required=False, allow_null=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
   

    def validate_email(self, value):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)

        if request and request.method == 'POST':
            customer = Customer.objects.filter(email__iexact=value).first() 

            if customer:
                if not customer.is_verified:
                    Send_Otp_Mail(customer.id)
                    raise serializers.ValidationError({
                        "message": "Email exists but is not verified. We have sent an OTP on your email, Please verify your email."
                    })

                raise serializers.ValidationError({
                    "error": "Email already exists."
                })

            return value  # valid new email

        if instance:
            # If the user is keeping the same email — allow it
            if instance.email.lower() == value.lower():
                return value

            # If changing to another email — make sure it's unique
            if Customer.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError({"error":"This email is already registered."})

        return value  # ensure return in all paths
                
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "username",
            "email",
            "user_role",
            "password",
            "is_verified",
            "venue_name",
            "venue_logo",
            "address",
            "phone",
        ]
        read_only_fields=["date_joined"]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user_role = validated_data.get('user_role', None)
        venue_name = validated_data.pop('venue_name', None)
        venue_logo = validated_data.pop('venue_logo', None)
        address = validated_data.pop('address', None)
        phone = validated_data.pop('phone', None)
        instance = Customer(**validated_data)

        if password:
            instance.set_password(password)  # Hash if updated
        
        instance.is_verified = True
        instance.save()
        
        if user_role =='1':
            Customer_profile.objects.get_or_create(customer=instance)
        
        if user_role =='2':
            venue, created = Venue_Info.objects.get_or_create(venue=instance)
            if created:
                time_not_set = "Not Set"
                Venue_Opening_Hours.objects.create(venue=instance, monday=time_not_set, tuesday=time_not_set, wednesday=time_not_set, thursday=time_not_set, friday=time_not_set,saturday=time_not_set,sunday=time_not_set)
                
            if venue_name:
                venue.venue_name = venue_name
            if venue_logo:
                venue.venue_logo = venue_logo
            if address:
                venue.address = address
            if phone:
                venue.phone = phone
            venue.save()
        
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # Hash if updated

        instance.save()
        
        return instance
    
    