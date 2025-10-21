from rest_framework.views import APIView
from rest_framework import generics
from venue.models.rewards import Rewards
from venue.Serializers.rewards_serializer import RewardsSerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only

class RewardsGetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Rewards.objects.filter(is_approved='approved')
    serializer_class = RewardsSerializer




class RewardsRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Rewards.objects.filter(is_approved='approved')
    serializer_class = RewardsSerializer