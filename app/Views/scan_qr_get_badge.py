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

class Scan_qr_get_badge(generics.CreateAPIView):

    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Challenge_Achiever.objects.all()
    serializer_class = ChallengeAchieverSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        achievement = serializer.save()

        challenge = achievement.challenge
        
        return Response({
            "badge_id": challenge.badge.badge.id,
            "badge_img": request.build_absolute_uri(challenge.badge.badge.image.url) if challenge.badge.badge.image else None,
            "message": (
                f"🎉👏 You earned a new badge {challenge.badge.badge.name} "
                f"and won {challenge.badge.badge.points_per_task} points!"
            ),
        }, status=status.HTTP_201_CREATED)

    


