from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from venue.Serializers.rewards_serializer import RewardsSerializer
from venue.models import rewards
from venue.models.rewards import Rewards
from rest_framework.parsers import MultiPartParser, FormParser

class Venue_Rewards(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        rewards = Rewards.objects.filter(venue__id=id)
        serializer = RewardsSerializer(rewards, many=True)
        
        return Response({"rewards": serializer.data})