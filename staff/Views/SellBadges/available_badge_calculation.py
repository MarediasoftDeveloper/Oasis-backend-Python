from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from app.models import Customer
from app.models import Customer_profile
from app.Models.earned_badges_by_user import Earned_Badges

from staff.models.badge_value_into_points import PointsPerBadge



def get_point_per_badge() -> int:
    
    value = PointsPerBadge.objects.first()
    if not value:
        raise ValidationError({"error":"Points Per Badge not configured"})

    return value.points_per_badge 


def calculate_points(badges: int, available_badges) -> int:
    
    if badges <= available_badges :
        raise ValidationError({"error":"You don't have enough badges for this request"})

    point_per_badge = get_point_per_badge()
    return point_per_badge * available_badges





class AvailableBadgesSellCalculation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        user = request.user
        available_badges = Earned_Badges.objects.filter(user=user).count()
        per_badge_value = get_point_per_badge() 

        return Response({
            'available_badges':available_badges,
            'per_badge_value':per_badge_value
        })
    
    def post(self, request):
        user = request.user
        amount_of_badges = request.data.get('number_of_bagdes')
        available_badges = Earned_Badges.objects.filter(user=user).count()
        total_badge_value = calculate_points(amount_of_badges, available_badges)

        badges_to_delete = Earned_Badges.objects.filter(user=user)[0:int(amount_of_badges)]
        profile = Customer_profile.objects.filter(customer=user).first()
        badges_to_delete.delete()
        
        profile.total_redeemed_points += total_badge_value
        profile.save()

        return Response({
            'message':f"Congratulations! you have got total {total_badge_value} points.",
        })
    



