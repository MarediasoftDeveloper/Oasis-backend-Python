from rest_framework import serializers
from venue.models.challenges import Challenges


class ChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenges
        fields = '__all__'
        read_only_fields=['venue']
    
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
        challenge = Challenges(**validated_data)
        
        return challenge

    def update(self, instance, validated_data):
        """Update an existing Challenge."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()
