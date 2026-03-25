from rest_framework import generics, status
from ..Models.challenge_achiever import Challenge_Achiever
from venue.models.challenges import Challenges
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Views.functions.referrals_utils import add_points_to_user
from app.models import Customer_profile
from app.Serializers.challenge_achiever_serializer import ChallengeAchieverSerializer
from rest_framework.serializers import Serializer
from venue.models.badges import BadgesLevel
from app.Models.earned_points import Earned_Points
from app.Models.earned_badges_by_user import Earned_Badges
from app.models import Customer_profile



class Scan_qr_get_badge(generics.CreateAPIView):

    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Challenge_Achiever.objects.all()
    serializer_class = ChallengeAchieverSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        achievement = serializer.save()
        
        challenge = achievement.challenge
        actual_badge = challenge.badge.badge
     
        earned_badges = Earned_Badges.objects.filter(user=self.request.user, badge=actual_badge).count()
        badge_category = BadgesLevel.objects.filter(badge=actual_badge).order_by('points_per_task')
       
        badge_img = None
        points_per_task=0


       

        for category in badge_category:
                if category.category.num_of_task_to_achieve_badge < earned_badges:
                    points_per_task= category.points_per_task
                    badge_img= category.image
                else:
                    points_per_task= category.points_per_task
                    badge_img= category.image
                    break

   
        return Response({
            "badge_id": actual_badge.id,
            "badge_img": request.build_absolute_uri(badge_img.url) if badge_img else None,
            "message": (
                f"🎉👏 You earned a new badge {actual_badge.name} "
                f"and won {points_per_task} points!"
            ),
        }, status=status.HTTP_201_CREATED)

    


