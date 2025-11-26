from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..Models.referrals import Referrals
from .functions.referrals_utils import get_reward_points, record_earned_points, update_customer_profiles_after_refferal_completion
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.models import Customer


def UseReferralCode(customer, referral_code):
    code = referral_code
    
    if not code:
        return {"error": "Referral code is required", "status": 400}

    try:
        referral = Referrals.objects.get(referral_code__iexact=code)
    except Referrals.DoesNotExist:
        return {"error": "Invalid referral code", "status": 404}

    # if referral.is_used:
    #     return {"error": "This referral code has already been used", "status": 400}

    if referral.referral_code_sender == customer:
        return {"error": "You cannot use your own referral code", "status": 400}


    # Mark as used
    # referral.is_used = True
    # referral.referral_code_user = customer
    # referral.save()

    get_points = get_reward_points()
    record_earned_points(referral.referral_code_sender, customer, get_points)
    update_customer_profiles_after_refferal_completion(referral.referral_code_sender, customer, get_points)
    
    return {"message": f"Congratulations! You got {get_points} points!", "status": 200}
