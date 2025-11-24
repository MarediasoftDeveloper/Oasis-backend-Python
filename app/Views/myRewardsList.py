from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.rewards_achiever import Rewards_Achiever
from venue.Serializers.rewards_serializer import RewardsSerializer
from app.Serializers.rewards_achiever_serializer import GetRewardsAchievmentsSerializer



class Achieved_Rewards_List(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    serializer_class=GetRewardsAchievmentsSerializer

    def get_queryset(self):
        return Rewards_Achiever.objects.filter(customer_taken=self.request.user).order_by('-achieved_at')
   