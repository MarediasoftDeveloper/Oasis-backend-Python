from rest_framework import serializers
from venue.models.challenges import Challenges

class ChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenges
        fields = '__all__'

    def validate_title(self, value):
        """Ensure challenge title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate(self, data):
        """Minimal logical checks."""
        start = data.get('starting_date')
        end = data.get('ending_date')
        cool_down = data.get('cool_down_hours')
        daily_cap = data.get('daily_cap')

        # Ensure end date is not before start date
        if start and end and end < start:
            raise serializers.ValidationError({
                'ending_date': 'Ending date cannot be earlier than starting date.'
            })

        # Ensure positive numbers
        if cool_down is not None and cool_down <= 0:
            raise serializers.ValidationError({
                'cool_down_hours': 'Cool down hours must be greater than 0.'
            })

        if daily_cap is not None and daily_cap <= 0:
            raise serializers.ValidationError({
                'daily_cap': 'Daily cap must be greater than 0.'
            })

        return data

    def create(self, validated_data):
        """Create a new Challenge."""
        return Challenges.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing Challenge."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()
