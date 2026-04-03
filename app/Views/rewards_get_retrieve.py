from rest_framework.views import APIView
from rest_framework import generics
from venue.models.rewards import Rewards
from venue.Serializers.rewards_serializer import RewardsSerializer
from app.Models.rewards_achiever import Rewards_Achiever
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework.response import Response
from venue.models.venue_info import Venue_Info


class RewardsGetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    serializer_class = RewardsSerializer

    def list(self, request, *args, **kwargs):
        queryset = Rewards.objects.filter(is_approved='approved')
        data=[]
        rewards_count = len(queryset)
        serialized=self.get_serializer(queryset)
        data = []
        for reward in queryset:
            # Count how many times this reward has been achieved
            rewards_achieve_count = Rewards_Achiever.objects.filter(reward=reward).count()

            # Serialize the reward itself
            serialized_reward = RewardsSerializer(reward).data  # Serializing the reward object
            venue_profile = Venue_Info.objects.filter(venue=reward.venue).first()
            # Add the achiever count to the serialized reward data
        
            serialized_reward["venue_name"] = venue_profile.venue_name if venue_profile else None
            serialized_reward["rewards_achieved_by"] = rewards_achieve_count

            data.append(serialized_reward)

        # Return the response
        return Response({
            "rewards_count": rewards_count,
            "rewards": data  # Use 'data' instead of serialized.data here

        })


class RewardsRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Rewards.objects.filter(is_approved='approved')
    serializer_class = RewardsSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get the reward instance
        reward = self.get_object()

        # Count how many times this reward has been achieved
        rewards_achieve_count = Rewards_Achiever.objects.filter(reward=reward).count()
        venue_profile = Venue_Info.objects.get(venue=reward.venue)
            # Add the achiever count to the serialized reward data
        # Serialize the reward
        serialized_reward = self.get_serializer(reward).data

        # Add the achieved count to the serialized reward
        serialized_reward["venue_name"] = venue_profile.venue_name
        serialized_reward["rewards_achieved_by"] = rewards_achieve_count

        # Return the response with the serialized data and achieved count
        return Response(serialized_reward)