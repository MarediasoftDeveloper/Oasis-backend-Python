from rest_framework.views import APIView
from rest_framework import generics
from ..Models.referrals import Referrals
from app.Serializers.referral_code_invite import Referral_Code_Serializer
import string
import random
from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.Permissions.send_by_customer_only import Request_By_Customer_Only

def generate_referral_code():
    """
    Generate a unique 8-character referral code.
    Example: 'A1X9QZ7P'
    """
    length = 8
    characters = string.ascii_uppercase + string.digits  # e.g. A-Z, 0-9
    code = get_random_string(length=length, allowed_chars=characters)

    # Ensure it's unique
    while Referrals.objects.filter(referral_code=code).exists():
        code = get_random_string(length=length, allowed_chars=characters)

    return code


class Send_Invite(APIView):

    permission_classes = [IsAuthenticated, Request_By_Customer_Only]

    def get(self, request):
        user = request.user

        # Check if user already has a referral code
        referral= Referrals.objects.create(
            referral_code_sender=user,
            referral_code=generate_referral_code(),
        )

        return Response({
            "referral_code": referral.referral_code,
        })

        

