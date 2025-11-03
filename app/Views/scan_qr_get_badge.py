from rest_framework import generics
from ..Models.challenge_achiever import Challenge_Achiever
from venue.models.challenges import Challenges
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Views.functions.referrals_utils import add_points_to_user
from app.models import Customer_profile
from app.Serializers.challenge_achiever_serializer import ChallengeAchieverSerializer


class Scan_qr_get_badge(generics.CreateAPIView):

    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Challenge_Achiever.objects.all()
    serializer_class = ChallengeAchieverSerializer

    

