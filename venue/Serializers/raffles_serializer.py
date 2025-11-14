from rest_framework import serializers
from venue.models.raffles import Raffles

class RafflesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raffles
        fields = '__all__'

    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate(self, data):
        """Basic, necessary validations."""
        start_date = data.get('start_date')
        rewarded_points = data.get('rewarded_points')
        points_to_join = data.get('points_to_join')

        # Ensure numeric logic makes sense
        if rewarded_points is not None and rewarded_points < 0:
            raise serializers.ValidationError({
                'error': 'Rewarded points cannot be negative.'
            })

        if points_to_join < 0:
            raise serializers.ValidationError({
                'error': 'Points to join cannot be negative.'
            })

        return data

    def create(self, validated_data):
        """Create new raffle entry."""
        return Raffles.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update raffle entry."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with future custom logic."""
        instance.delete()
