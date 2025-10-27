from rest_framework import serializers
from venue.models.venue_info import Venue_Info
import re
from app.Serializers.customer_signup_serializer import Customer_Serializer


class VenueInfoSerializer(serializers.ModelSerializer):
    venue= Customer_Serializer()
    class Meta:
        model = Venue_Info
        fields = '__all__'

    def validate_venue_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Venue name cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError("Venue name must be at least 3 characters long.")
        return value

    def validate_phone(self, value):
     
        e164_pattern = re.compile(r'^\+?[1-9]\d{7,14}$')

        if not e164_pattern.match(value):
            raise serializers.ValidationError(
                "Enter a valid phone number in international format "
                "(e.g. +64211234567 or +14155552671)."
            )
        return value

    def validate(self, data):
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is not None and not (-90 <= latitude <= 90):
            raise serializers.ValidationError({"latitude": "Latitude must be between -90 and 90."})
        if longitude is not None and not (-180 <= longitude <= 180):
            raise serializers.ValidationError({"longitude": "Longitude must be between -180 and 180."})

        status = data.get('status')
        valid_statuses = [choice[0] for choice in getattr(self.Meta.model, 'STATUS_CHOICES', [])]
        if status not in valid_statuses:
            raise serializers.ValidationError({"status": f"Invalid status '{status}'."})

        return data


    def create(self, validated_data):
        """Custom create logic if needed (optional)."""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()
        return instance