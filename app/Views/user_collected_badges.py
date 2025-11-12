from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from rest_framework import status
from ..Models.earned_badges_by_user import Earned_Badges
from venue.models. venue_badges import Venue_Badges
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
from datetime import datetime


# class Collected_badges(APIView):
#     permission_classes=[IsAuthenticated]

#     def get(self, request):
        
#         collected_badges = Venue_Badges.objects.all(is_active=True)
#         if collected_badges:
#             for badge in collected_badges:

        
