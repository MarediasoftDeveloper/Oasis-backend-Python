from rest_framework.views import APIView
from rest_framework import generics
from venue.models.challenges import Challenges
from app.Models.challenge_achiever import Challenge_Achiever
from venue.Serializers.challenge_serializer import ChallengesSerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework.response import Response




class GetChallengeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Challenges.objects.filter(is_approved='approved')
    serializer_class = ChallengesSerializer




class GetChallengeObjView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Challenges.objects.filter(is_approved='approved')
    serializer_class = ChallengesSerializer