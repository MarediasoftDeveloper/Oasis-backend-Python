from rest_framework import serializers
from venue.models.rewards import Rewards
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
        print(badge_ids)
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


# class VenueRewardsSerializer(serializers.ModelSerializer):
#     venue = VenueInfoSerializer(source="venue.venue_profile")
#     class Meta:
#         model = Rewards
#         fields = '__all__'
        

#     def validate_title(self, value):
#         """Ensure title is not empty."""
#         if not value or not value.strip():
#             raise serializers.ValidationError("Title cannot be empty.")
#         return value

#     def validate(self, data):
#         """Only necessary cross-field checks."""
#         start = data.get('started_at')
#         end = data.get('ended_at')

#         # Check date order if both provided
#         if start and end and end < start:
#             raise serializers.ValidationError({
#                 'ended_at': 'End date cannot be earlier than start date.'
#             })

#         return data

#     def create(self, validated_data):
#         """Handle reward creation."""
#         return Rewards.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         """Handle reward updates."""
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance

#     def delete(self, instance):
#         """Allow deletion with possible custom logic later."""
#         instance.delete()
