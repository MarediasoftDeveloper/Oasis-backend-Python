from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from venue.Serializers.challenge_serializer import ChallengesSerializer
from venue.Serializers.badges_serializer import BadgesSerializer
from rest_framework import status
from ..Models.earned_badges_by_user import Earned_Badges
from venue.models.badges import Badges
from venue.models.challenges import Challenges
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
from datetime import datetime


class Collected_badges(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        
        data=[]
        earned_badges = Earned_Badges.objects.filter(user=self.request.user)
        earned_badges_ids = earned_badges.distinct().values_list('badge__id', flat=True)
        for earned in earned_badges_ids:
            badge_count = earned_badges.filter(badge__id=earned).count()
            badge = Badges.objects.filter(id=earned)
            data.append({
              "collected_badges":{
                "badge": BadgesSerializer(badge, many=True).data,
                "collected_badge_count":badge_count,
              }  
            })
        unearned_badges = Badges.objects.filter().exclude(id__in=earned_badges_ids)
        data.append({
            "uncollected_badges":BadgesSerializer(unearned_badges, many=True).data,
        })

       

        return Response(data)
                