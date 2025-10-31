from rest_framework.views import APIView
from rest_framework import generics
from venue.models.rewards import Rewards
from venue.Serializers.rewards_serializer import RewardsSerializer
from app.Models.rewards_achiever import Rewards_Achiever
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from rest_framework.response import Response

class MyRewardsGetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]
    serializer_class = RewardsSerializer

    def list(self, request, *args, **kwargs):
        queryset = Rewards.objects.filter(venue=request.user, is_approved='approved')
        data=[]
        rewards_count = len(queryset)
        serialized=self.get_serializer(queryset)
        data = []
        for reward in queryset:
            # Count how many times this reward has been achieved
            rewards_achieve_count = Rewards_Achiever.objects.filter(reward=reward).count()

            # Serialize the reward itself
            serialized_reward = RewardsSerializer(reward).data  # Serializing the reward object

            # Add the achiever count to the serialized reward data
            serialized_reward["rewards_achieved_by"] = rewards_achieve_count
            data.append(serialized_reward)

        # Return the response
        return Response({
            "rewards_count": rewards_count,
            "rewards": data  # Use 'data' instead of serialized.data here
        })


class MyRewardsRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]
    serializer_class = RewardsSerializer

    def get_queryset(self):
        return Rewards.objects.filter(venue=self.request.user, is_approved='approved')

    def retrieve(self, request, *args, **kwargs):
        # Get the reward instance
        reward = self.get_object()

        # Count how many times this reward has been achieved
        rewards_achieve_count = Rewards_Achiever.objects.filter(reward=reward).count()

        # Serialize the reward
        serialized_reward = self.get_serializer(reward).data

        # Add the achieved count to the serialized reward
        serialized_reward["rewards_achieved_by"] = rewards_achieve_count

        # Return the response with the serialized data and achieved count
        return Response(serialized_reward)