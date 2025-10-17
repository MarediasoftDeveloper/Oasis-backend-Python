from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..Models.referrals import Referrals
from .functions.referrals_utils import get_reward_points, record_earned_points, update_customer_profiles
from app.Permissions.send_by_customer_only import Request_By_Customer_Only

class UseReferralCode(APIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]

    def post(self, request):
        code = request.data.get("referral_code")

        if not code:
            return Response({"error": "Referral code is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            referral = Referrals.objects.get(referral_code=code)
        except Referrals.DoesNotExist:
            return Response({"error": "Invalid referral code"}, status=status.HTTP_404_NOT_FOUND)

        # Check if code already used
        if referral.is_used:
            return Response({"error": "This referral code has already been used"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent self-referral (optional)
        if referral.referral_code_sender == request.user:
            return Response({"error": "You cannot use your own referral code"}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as used
        referral.is_used = True
        referral.referral_code_user = request.user
        referral.save()

        get_points = get_reward_points()
        record = record_earned_points(referral.referral_code_sender, referral.referral_code_user, get_points)
        add_points_customer_profile = update_customer_profiles(referral.referral_code_sender, referral.referral_code_user, get_points)
        
        


        return Response({
            "message": f"Congratulations! you got {get_points} points!",
        }, status=status.HTTP_200_OK)
