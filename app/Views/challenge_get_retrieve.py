from rest_framework.views import APIView
from rest_framework import generics
from venue.models.challenges import Challenges
from app.Models.challenge_achiever import Challenge_Achiever
from venue.Serializers.challenge_serializer import ChallengesSerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework.response import Response

class ChallengeGetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    serializer_class = ChallengesSerializer

    def list(self, request, *args, **kwargs):
        queryset = Challenges.objects.filter(is_approved='approved')

        data = []
        for challenge in queryset:
            # Count achievers for this challenge
            challenges_achieve_count = Challenge_Achiever.objects.filter(challenge=challenge).count()

            # Serialize challenge
            serialized_challenge = self.get_serializer(challenge).data

            # Add custom field
            serialized_challenge["challenge_achieved_by"] = challenges_achieve_count
            data.append(serialized_challenge)

        # Return proper response
        return Response({
            "challenge_count": len(queryset),
            "challenges": data
        })

class ChallengeRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Challenges.objects.filter(is_approved='approved')
    serializer_class = ChallengesSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get the reward instance
        challenge = self.get_object()

        # Count how many times this reward has been achieved
        challenge_achieve_count = Challenge_Achiever.objects.filter(challenge=challenge).count()

        # Serialize the reward
        serialized_reward = self.get_serializer(challenge).data

        # Add the achieved count to the serialized reward
        serialized_reward["challenge_achieved_by"] = challenge_achieve_count

        # Return the response with the serialized data and achieved count
        return Response(serialized_reward)