from rest_framework import serializers
from venue.models.challenges import Challenges
from venue.models.qr_info_model import QR_Info
from venue.Serializers.qr_info_serializer import QRInfoSerializer
from venue.Serializers.venue_badges_serializer import VenueBadgesSerializer
from venue.models.venue_badges import Venue_Badges
from app.Serializers.customer_signup_serializer import Customer_Serializer


class ChallengesSerializer(serializers.ModelSerializer):
    winning_points = serializers.IntegerField(min_value=5, required=True, write_only=True)
    qr_code = QRInfoSerializer(read_only=True)
    venue = Customer_Serializer(read_only=True)
    badge_info = VenueBadgesSerializer(read_only=True)
    badge = serializers.PrimaryKeyRelatedField(
        queryset=Venue_Badges.objects.all(),
        required=True
    )
    class Meta:
        model = Challenges
        fields = '__all__'
        read_only_fields=['venue', 'qr_code', 'badge_info']
    
    # Custom validation to check if the starting date is before the ending date
    def validate(self, data):
        """Ensure that the ending date is after the starting date."""
        starting_date = data.get('starting_date')
        ending_date = data.get('ending_date')
        
        if ending_date and starting_date and ending_date < starting_date:
            raise serializers.ValidationError("Ending date cannot be before the starting date.")
        
        return data

    def validate_daily_times(self, value, field_name):
        """Ensure daily_open_time and daily_close_time are within valid range."""
        if value:
            if value.hour < 0 or value.hour >= 24 or value.minute < 0 or value.minute >= 60:
                raise serializers.ValidationError(f"{field_name} must be a valid time (HH:MM format).")
        return value

    def validate_daily_open_time(self, value):
        """Validate that daily open time is a valid time."""
        return self.validate_daily_times(value, "daily_open_time")

    def validate_daily_close_time(self, value):
        """Validate that daily close time is a valid time."""
        return self.validate_daily_times(value, "daily_close_time")


    def create(self, validated_data):
        """Create a new Challenge."""
        winning_points = validated_data.pop('winning_points')
        ending_at = validated_data.get('ending_at')
        qr_obj = QR_Info(winning_points=winning_points, expires_at=ending_at)
        qr_obj.save()
      
        
        
        return Challenges.objects.create(
            qr_code = qr_obj,
            **validated_data
        )

    def update(self, instance, validated_data):
        """Update an existing Challenge."""
        winning_points = validated_data.pop('winning_points')
        

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if winning_points:
            instance.qr_code.winning_points=winning_points
            
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()
