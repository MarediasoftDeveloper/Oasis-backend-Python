from rest_framework import serializers
from venue.models.rewards import Rewards

class RewardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rewards
        fields = '__all__'

    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate(self, data):
        """Only necessary cross-field checks."""
        start = data.get('started_at')
        end = data.get('ended_at')

        # Check date order if both provided
        if start and end and end < start:
            raise serializers.ValidationError({
                'ended_at': 'End date cannot be earlier than start date.'
            })

        return data

    def create(self, validated_data):
        """Handle reward creation."""
        return Rewards.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Handle reward updates."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible custom logic later."""
        instance.delete()
