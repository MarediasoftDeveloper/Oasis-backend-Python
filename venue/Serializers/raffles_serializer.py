from rest_framework import serializers
from venue.models.raffles import Raffles
from venue.models.raffles import Raffles
from app.models import Customer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer

class RafflesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Raffles
        fields = '__all__'
        read_only_fields=['is_approved', 'venue']

    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error":"Title cannot be empty."})
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






class RafflesStaffSerializer(serializers.ModelSerializer):
    venue = VenueInfoSerializer(source="venue.venue_profile", read_only=True)
    venue_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(user_role='2'),
        write_only=True,
        required=False
    )
    class Meta:
        model = Raffles
        fields = '__all__'
        read_only_fields=['is_approved', 'venue']

    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error":"Title cannot be empty."})
        return value
    
    def validate_description(self, value):
        """Ensure description is not too long."""
        if value and len(value) > 1000:
            raise serializers.ValidationError({"error":"Description is too long."})
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
        venue = validated_data.pop('venue_id')
         
        return Raffles.objects.create(venue=venue, **validated_data)

    def update(self, instance, validated_data):
        """Update raffle entry."""
        venue = validated_data.pop('venue_id')
        if venue:
            instance.venue = venue

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with future custom logic."""
        instance.delete()