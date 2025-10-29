from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from rest_framework import status
from ..Models.earned_badges_by_user import Earned_Badges
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
from datetime import datetime


class User_Badges_Record(APIView):

    permission_classes=[IsAuthenticated]

    def get(self, request, id):
       

        pass

