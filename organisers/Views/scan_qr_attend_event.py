from rest_framework import generics, status

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Views.functions.referrals_utils import add_points_to_user
from app.models import Customer_profile
from app.Models.event_badges_earned import EventBadgesEarned
from organisers.serializers.event_badge_earned_serializer import EventBadgeEarnedSerializer
from venue.models.badges import BadgesLevel
from app.Models.earned_points import Earned_Points
from app.Models.event_badges_earned import EventBadgesEarned
from app.models import Customer_profile


class Scan_qr_attend_event(generics.CreateAPIView):

    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = EventBadgesEarned.objects.all()
    serializer_class = EventBadgeEarnedSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        achievement = serializer.save()
        
        event = achievement.event
        print(event)
        actual_badge = event.badge
        print(actual_badge)
        earned_badges = EventBadgesEarned.objects.filter(user=request.user, event=event).count()
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

    


