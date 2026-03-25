from rest_framework import serializers
from venue.models.rewards import Rewards
from app.models import Customer
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.models.badges import Badges
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
 

class RewardsSerializer(serializers.ModelSerializer):
    
    rewards_for_badge_holder = BadgesSerializer(many=True, read_only=True)
    rewards_for_badge_holder_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Badges.objects.all(),
        write_only=True,
        required=False
    )
    class Meta:
        model = Rewards
        fields = '__all__'
        read_only_fields=['venue']


    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error":"Title cannot be empty."})
        return value

    

    def validate(self, data):
        """Only necessary cross-field checks."""
        start = data.get('started_at')
        end = data.get('ended_at')

        # Check date order if both provided
        if start and end and end < start:
            raise serializers.ValidationError({
                'error': 'End date cannot be earlier than start date.'
            })

        return data

    def create(self, validated_data):
        badge_ids = validated_data.pop('rewards_for_badge_holder_ids', [])
        reward = Rewards.objects.create(**validated_data)

        # Add many-to-many relationships
        if badge_ids:
            reward.rewards_for_badge_holder.set(badge_ids)

        return reward

    def update(self, instance, validated_data):
        badge_ids = validated_data.pop('rewards_for_badge_holder_ids', None)
        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update many-to-many only if provided
        if badge_ids is not None:
            instance.rewards_for_badge_holder.set(badge_ids)

        return instance
    
    def delete(self, instance):
        """Allow deletion with possible custom logic later."""
        instance.delete()


class StaffRewardsSerializer(serializers.ModelSerializer):
    venue = VenueInfoSerializer(source="venue.venue_profile", read_only=True) 
    venue_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(user_role='2'),
        write_only=True,
        required=False
    )
    rewards_for_badge_holder = BadgesSerializer(many=True, read_only=True)
    rewards_for_badge_holder_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Badges.objects.all(),
        write_only=True,
        required=False
    )
    class Meta:
        model = Rewards
        fields = '__all__'
        read_only_fields=['venue']


    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error":"Title cannot be empty."})
        return value

    def validate_condition(self, value):
        """Ensure condition is not empty."""
        if value and len(value) > 1000:
            raise serializers.ValidationError({"error":"Description is too long."})
        return value
    
    
    def validate(self, data):
        """Only necessary cross-field checks."""
        start = data.get('started_at')
        end = data.get('ended_at')
        venue_id = data.get('venue_id')

        if venue_id is None:
            raise serializers.ValidationError({
                'error': 'Please Select the Venue for which you want to create a Reward.'
            })
        # Check date order if both provided
        if start and end and end < start:
            raise serializers.ValidationError({
                'error': 'End date cannot be earlier than start date.'
            })

        return data

    def create(self, validated_data):
        badge_ids = validated_data.pop('rewards_for_badge_holder_ids', [])
        venue = validated_data.pop('venue_id')
      
        reward = Rewards.objects.create(venue=venue, **validated_data)
        # Add many-to-many relationships
        if badge_ids:
            reward.rewards_for_badge_holder.set(badge_ids)



        return reward

    def update(self, instance, validated_data):
        badge_ids = validated_data.pop('rewards_for_badge_holder_ids', None)
        venue = validated_data.pop('venue_id')
      
        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if venue:
            instance.venue=venue
        instance.save()

        # Update many-to-many only if provided
        if badge_ids is not None:
            instance.rewards_for_badge_holder.set(badge_ids)

        return instance
    
    def delete(self, instance):
        """Allow deletion with possible custom logic later."""
        instance.delete()