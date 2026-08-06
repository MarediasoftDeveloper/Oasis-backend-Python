from rest_framework import serializers
from venue.models.rewards import Rewards
from venue.Serializers.rewards_serializer import RewardsSerializer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.utils import timezone


class GetRewardSerializerStaff(serializers.ModelSerializer):
    
    class Meta:
        model = Rewards
        fields=["title"]
