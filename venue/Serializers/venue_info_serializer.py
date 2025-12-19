from rest_framework import serializers
from venue.models.venue_info import Venue_Info
from app.models import Customer
import re
from venue.Serializers.venue_signup_serializer import Venue_SignUp_Serializer


class VenueInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=25, allow_blank=True, write_only=True)
    password = serializers.CharField(max_length=50, allow_blank=True, write_only=True)
    venue= Venue_SignUp_Serializer(read_only=True)

    class Meta:
        model = Venue_Info
        fields = '__all__'
        read_only_fields=['status']

   
    
    def validate_venue_name(self, value):
        if not value.strip():
            raise serializers.ValidationError({"error":"Venue name cannot be empty."})
        if len(value) < 3:
            raise serializers.ValidationError({"error":"Venue name must be at least 3 characters long."})
        return value

    def validate_phone(self, value):
        if not value or len(value) > 15:
            raise serializers.ValidationError(
                "Enter a valid phone number (landline or mobile, with optional +country code)."
            )

        return value

    def validate(self, data):
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude is not None and not (-90 <= latitude <= 90):
            raise serializers.ValidationError({"latitude": "Latitude must be between -90 and 90."})
        if longitude is not None and not (-180 <= longitude <= 180):
            raise serializers.ValidationError({"longitude": "Longitude must be between -180 and 180."})


        return data


    def create(self, validated_data):
        """Custom create logic if needed (optional)."""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        username = validated_data.get("username", None)
       

        # Validate username
        if username and username.lower() != instance.venue.username.lower():
            if Customer.objects.filter(username__iexact=username).exists():
                raise serializers.ValidationError({
                    "error": "This Username already exists, try something more unique!"
                })
            instance.venue.username = username

        # Update password
        if password:
            instance.venue.set_password(password)

        # Update other fields in instance (excluding special fields)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save both profile + instance
        instance.venue.save()
        instance.save()

        return instance