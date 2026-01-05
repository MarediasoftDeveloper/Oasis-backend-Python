from rest_framework import serializers
from app.Models.rewards_achiever import Rewards_Achiever
from app.Models.earned_badges_by_user import Earned_Badges
from venue.models.badges import BadgesLevel
from app.models import Customer_profile
from venue.Serializers.rewards_serializer import RewardsSerializer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.utils import timezone

class RewardsAchieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rewards_Achiever
        fields = '__all__'
        read_only_fields=['customer_taken']


    def validate(self, data):
        """Ensure a customer can't claim the same reward multiple times."""
        customer = self.context.get('request').user
        customer_profile = Customer_profile.objects.get(customer=customer)
        reward = data.get('reward')
        rewards_achieved = Rewards_Achiever.objects.filter(reward=reward).count()
        # Check only on creation (not update)
        if self.instance is None and Rewards_Achiever.objects.filter(customer_taken=customer, reward=reward).exists():
            raise serializers.ValidationError({
                "error": "This reward has already been achieved by you."
            })

        if not customer_profile.total_redeemed_points >= reward.required_points_for_reward:
                raise serializers.ValidationError({
                    "error": "You do not have enough points to get this reward!"
                })

        if reward.started_at > timezone.now():
                raise serializers.ValidationError({
                    "error": "The reward has not started yet."
                })

        # Check if the raffle has ended (ended_at <= current time)
        if reward.ended_at < timezone.now():
            reward.is_ended=True
            reward.save()
            raise serializers.ValidationError({
                "error": "This reward has ended. You can no longer join."
            })
        
        if reward.is_ended:
            raise serializers.ValidationError({
                "error": "This reward has ended. You can no longer join."
            })
        

        if rewards_achieved > reward.stock:
            raise serializers.ValidationError({
                "error": "This reward has been reached its maximum numbers of achievers!"
            })
        
        if not reward.is_approved == 'approved':
            raise serializers.ValidationError({
                "error": "This reward has been suspended or not approved yet!"
            })
        

        

        return data

    def create(self, validated_data):
        """Create a new Rewards_Achiever record."""
        return Rewards_Achiever.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update existing Rewards_Achiever record."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible custom logic later."""
        instance.delete()




class GetRewardsAchievmentsSerializer(serializers.ModelSerializer):
    reward = RewardsSerializer(read_only=True)
    customer_taken = CustomerProfileSerializer(source='customer_taken.customer_profile', read_only=True)

    class Meta:
        model = Rewards_Achiever
        fields = '__all__'
        read_only_fields=['customer_taken', 'reward']